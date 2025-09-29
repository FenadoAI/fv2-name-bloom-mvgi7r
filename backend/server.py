from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import hashlib
import secrets
import bcrypt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
import jwt

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Auth configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# User models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    favorites: List[str] = Field(default_factory=list)  # List of name IDs

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

# Name models
class Name(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    gender: str  # "boy", "girl", "unisex"
    origin: str
    meaning: str
    popularity_score: int = Field(default=50, ge=1, le=100)
    image_url: Optional[str] = None

class NameRequest(BaseModel):
    gender: Optional[str] = None  # "boy", "girl", "unisex", or None for all
    count: int = Field(default=10, ge=1, le=50)
    style: Optional[str] = None  # "traditional", "modern", "unique", etc.

class FavoritesList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name_ids: List[str]
    share_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    name_id: str

class ImageGenerationResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    error: Optional[str] = None

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# Authentication routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )

    await db.users.insert_one(user.dict())

    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at
    )

@api_router.post("/auth/login")
async def login_user(user_data: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"email": user_data.email})
    if not user_doc or not verify_password(user_data.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    access_token = create_access_token(data={"sub": user_doc["id"]})

    user = User(**user_doc)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        )
    }

# Name generation routes
@api_router.post("/names/generate", response_model=List[Name])
async def generate_names(request: NameRequest):
    """Generate baby names using AI"""
    global chat_agent

    try:
        # Initialize chat agent if needed
        if chat_agent is None:
            chat_agent = ChatAgent(agent_config)

        # Build prompt based on request parameters
        gender_filter = ""
        if request.gender:
            gender_filter = f" for {request.gender}s"

        style_filter = ""
        if request.style:
            style_filter = f" in {request.style} style"

        prompt = f"""Generate {request.count} baby names{gender_filter}{style_filter}.
        For each name, provide:
        - name: the actual name
        - gender: "boy", "girl", or "unisex"
        - origin: cultural/linguistic origin
        - meaning: what the name means
        - popularity_score: number from 1-100 indicating popularity (50 = average)

        Return only a JSON array of objects with these fields. No additional text."""

        # Get AI response
        result = await chat_agent.execute(prompt)

        if not result.success:
            raise HTTPException(status_code=500, detail="Failed to generate names")

        # Try to parse AI response as JSON
        import json
        try:
            names_data = json.loads(result.content)
            names = []
            for name_data in names_data:
                name = Name(
                    name=name_data.get("name", "Unknown"),
                    gender=name_data.get("gender", "unisex"),
                    origin=name_data.get("origin", "Unknown"),
                    meaning=name_data.get("meaning", "Unknown"),
                    popularity_score=name_data.get("popularity_score", 50)
                )
                names.append(name)
                # Store in database for future reference
                await db.names.insert_one(name.dict())

            return names
        except json.JSONDecodeError:
            # Fallback: create some sample names if AI response isn't valid JSON
            sample_names = [
                Name(name="Emma", gender="girl", origin="Germanic", meaning="Universal", popularity_score=95),
                Name(name="Liam", gender="boy", origin="Irish", meaning="Strong-willed warrior", popularity_score=92),
                Name(name="Olivia", gender="girl", origin="Latin", meaning="Olive tree", popularity_score=88),
                Name(name="Noah", gender="boy", origin="Hebrew", meaning="Rest, comfort", popularity_score=85),
                Name(name="Ava", gender="girl", origin="Latin", meaning="Life", popularity_score=82)
            ]

            # Store sample names and return subset based on request
            filtered_names = []
            for name in sample_names:
                if len(filtered_names) >= request.count:
                    break
                if not request.gender or name.gender == request.gender or name.gender == "unisex":
                    await db.names.insert_one(name.dict())
                    filtered_names.append(name)

            return filtered_names[:request.count]

    except Exception as e:
        logger.error(f"Error generating names: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating names: {str(e)}")

@api_router.post("/names/{name_id}/generate-image", response_model=ImageGenerationResponse)
async def generate_name_image(name_id: str, current_user: User = Depends(get_current_user)):
    """Generate an artistic image for a given name"""
    try:
        # Get the name from database
        name_doc = await db.names.find_one({"id": name_id})
        if not name_doc:
            raise HTTPException(status_code=404, detail="Name not found")

        name_obj = Name(**name_doc)

        # Create a descriptive prompt for the name
        gender_desc = "baby boy" if name_obj.gender == "boy" else "baby girl" if name_obj.gender == "girl" else "baby"
        prompt = f"Beautiful artistic illustration of the name '{name_obj.name}' written in elegant calligraphy, surrounded by soft pastel colors and gentle nature elements like flowers, stars, or clouds, perfect for a {gender_desc} nursery decoration. The name should be the focal point with beautiful typography, dreamy and peaceful atmosphere, soft lighting, watercolor style"

        # Use chat agent to generate image through MCP
        global chat_agent
        if chat_agent is None:
            chat_agent = ChatAgent(agent_config)

        # Create a prompt that instructs the agent to generate an image
        image_prompt = f"""Please generate an image with this description: {prompt}

        Use the image generation tool to create this image. Return only the image URL from the result."""

        result = await chat_agent.execute(image_prompt, use_tools=True)

        if result.success and result.content:
            # Try to extract URL from the response
            content = result.content.strip()

            # Look for URL patterns in the response
            import re
            url_patterns = [
                r'https://[^\s<>"\']+\.(?:jpg|jpeg|png|gif|webp|svg)',
                r'https://storage\.googleapis\.com/[^\s<>"\']+',
                r'"url"\s*:\s*"([^"]+)"',
                r"'url'\s*:\s*'([^']+)'"
            ]

            image_url = None
            for pattern in url_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    image_url = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    break

            # If no URL found, try to parse as JSON
            if not image_url:
                try:
                    import json
                    json_data = json.loads(content)
                    if isinstance(json_data, dict) and 'url' in json_data:
                        image_url = json_data['url']
                except:
                    pass

            if image_url:
                # Update name with image URL in database
                await db.names.update_one(
                    {"id": name_id},
                    {"$set": {"image_url": image_url}}
                )

                return ImageGenerationResponse(
                    success=True,
                    image_url=image_url
                )
            else:
                return ImageGenerationResponse(
                    success=False,
                    error=f"Could not extract image URL from response: {content}"
                )
        else:
            return ImageGenerationResponse(
                success=False,
                error=result.error or "Image generation failed"
            )

    except Exception as e:
        logger.error(f"Error generating image for name {name_id}: {e}")
        return ImageGenerationResponse(
            success=False,
            error=f"Error generating image: {str(e)}"
        )

# Favorites routes
@api_router.post("/favorites/add/{name_id}")
async def add_to_favorites(name_id: str, current_user: User = Depends(get_current_user)):
    """Add a name to user's favorites"""
    # Check if name exists
    name = await db.names.find_one({"id": name_id})
    if not name:
        raise HTTPException(status_code=404, detail="Name not found")

    # Add to user's favorites if not already there
    if name_id not in current_user.favorites:
        current_user.favorites.append(name_id)
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"favorites": current_user.favorites}}
        )

    return {"message": "Added to favorites"}

@api_router.delete("/favorites/remove/{name_id}")
async def remove_from_favorites(name_id: str, current_user: User = Depends(get_current_user)):
    """Remove a name from user's favorites"""
    if name_id in current_user.favorites:
        current_user.favorites.remove(name_id)
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"favorites": current_user.favorites}}
        )

    return {"message": "Removed from favorites"}

@api_router.get("/favorites", response_model=List[Name])
async def get_user_favorites(current_user: User = Depends(get_current_user)):
    """Get user's favorite names"""
    if not current_user.favorites:
        return []

    names = await db.names.find({"id": {"$in": current_user.favorites}}).to_list(100)
    return [Name(**name) for name in names]

@api_router.post("/favorites/share")
async def create_shareable_list(current_user: User = Depends(get_current_user)):
    """Create a shareable link for user's favorites"""
    favorites_list = FavoritesList(
        user_id=current_user.id,
        name_ids=current_user.favorites.copy()
    )

    await db.favorites_lists.insert_one(favorites_list.dict())

    return {
        "share_token": favorites_list.share_token,
        "share_url": f"/shared/{favorites_list.share_token}"
    }

@api_router.get("/shared/{share_token}", response_model=List[Name])
async def get_shared_favorites(share_token: str):
    """Get shared favorites list by token"""
    favorites_list = await db.favorites_lists.find_one({"share_token": share_token})
    if not favorites_list:
        raise HTTPException(status_code=404, detail="Shared list not found")

    if not favorites_list["name_ids"]:
        return []

    names = await db.names.find({"id": {"$in": favorites_list["name_ids"]}}).to_list(100)
    return [Name(**name) for name in names]

# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
