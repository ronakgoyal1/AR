import logging
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image, UnidentifiedImageError, ImageOps
from core.cv_pipeline import process_tryon

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Aura AI Try-On API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/try-on")
async def try_on_endpoint(
    image: UploadFile = File(...),
    earring_id: str = Form(...)
):
    try:
        logger.info(f"Received try-on request for earring: {earring_id}")
        
        contents = await image.read()
        if not contents:
            logger.error("Upload failed: Empty file received.")
            return JSONResponse(status_code=400, content={"success": False, "error": "Empty upload. Please provide a valid image file."})
        
        logger.info(f"Image received, size: {len(contents)} bytes")
        
        try:
            pil_image = Image.open(io.BytesIO(contents))
            # Critically handle EXIF orientation for mobile uploads
            pil_image = ImageOps.exif_transpose(pil_image)
            pil_image = pil_image.convert("RGB")
            logger.info(f"Image decoded successfully. Dimensions: {pil_image.width}x{pil_image.height}, Format: RGB")
        except UnidentifiedImageError:
            logger.error("Image decode failed: Unidentified format.")
            return JSONResponse(status_code=400, content={"success": False, "error": "Unsupported format. Please upload a valid JPEG or PNG image."})
        except Exception as e:
            logger.error(f"Image decode error: {str(e)}")
            return JSONResponse(status_code=400, content={"success": False, "error": "Failed to decode image."})
        
        logger.info("Starting CV pipeline processing...")
        result = process_tryon(pil_image, earring_id)
        logger.info("CV pipeline completed successfully.")
        
        return {"success": True, "results": result["variations"], "face_shape": result["face_shape"]}
    except ValueError as ve:
        logger.warning(f"CV Pipeline warning: {str(ve)}")
        return JSONResponse(status_code=422, content={"success": False, "error": str(ve)})
    except Exception as e:
        import traceback
        logger.error(f"Critical Backend Error:\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"success": False, "error": "Internal Server Error during AI processing."})

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
