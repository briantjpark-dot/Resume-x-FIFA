import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Import your orchestrator script and path configuration
from main import RESUME_PATH, build_card

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("Resume Card Builder")

app = FastAPI(title="Resume Card Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8800"],  
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/resumes/ratings")
def get_resume_ratings():
    
    logger.info("Received request to calculate resume ratings.")
    
    # PDF file does not exist
    if not RESUME_PATH.exists():
        msg = f"PDF file not found: '{RESUME_PATH.resolve()}'"
        logger.error(f"{msg}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )

    #Actual functionality
    try:
        logger.info(f"Processing resume '{RESUME_PATH.name}'...")
        ratings_data = build_card(RESUME_PATH)
        
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