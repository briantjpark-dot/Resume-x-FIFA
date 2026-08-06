import logging
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

# Import your orchestrator script
from main import build_card

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("Resume Card Builder")

app = FastAPI(title="Resume Card Builder API")

@app.get("/")
def get_frontend():
    return FileResponse("index.html")

@app.get("/frontend.js")
def get_frontend_js():
    return FileResponse("frontend.js", media_type="application/javascript")

@app.post("/score")
async def score_resume(file: UploadFile = File(...)):

    logger.info(f"Received resume upload '{file.filename}'.")

    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file must be a PDF."
        )

    #Actual functionality
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp.flush()
            tmp_path = Path(tmp.name)

            logger.info(f"Processing resume '{file.filename}'...")
            ratings_data = build_card(tmp_path)

        #Empty dict
        if not ratings_data:
            logger.error("Card build was finished but returned an empty dictionary.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Pipeline processed zero records."
            )

        logger.info("Pipeline execution successful.")
        return ratings_data

    except PermissionError as pe:
        #Can't read due to permissions
        logger.exception(f"Permission denied accessing resume files: {str(pe)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server lacks permission to read resume PDF files."
        )

    except (ValueError, KeyError) as ve:
        # format issues
        logger.exception(f"Data formatting error during parsing: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process or parse resume content: {str(ve)}"
        )

    except HTTPException:
        raise

    except Exception as e:
        # Catch-all for API timeouts, LLM failures, or unexpected errors
        logger.exception(f"Unexpected Error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal pipeline error [{type(e).__name__}]: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)