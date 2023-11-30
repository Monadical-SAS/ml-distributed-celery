from io import BytesIO
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.config.logger import InitLogger
from app.integrations.genai_generator import GenerativeAIGenerator
from app.models.schemas import GenRequest
from app.services.generation_service import GenerationService
from app.utils.images import from_image_to_bytes

app = FastAPI()

generator_service = GenerationService(generator=GenerativeAIGenerator())

config_path = Path("app/config").absolute() / "logging-conf.yaml"
logger = InitLogger.create_logger(config_path)

settings = get_settings()
ALLOWED_ORIGINS = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post('/generate')
async def generate():
    images = generator_service.generate_images_with_text2img(request=GenRequest())
    img_bytes = from_image_to_bytes(images[0])
    return StreamingResponse(BytesIO(img_bytes), media_type="image/png")
