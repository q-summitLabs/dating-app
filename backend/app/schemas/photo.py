from pydantic import BaseModel, Field


class PhotoUploadResponse(BaseModel):
    """Response model for photo upload."""

    url: str = Field(..., description="Public URL of the uploaded photo")
    s3_key: str = Field(..., description="S3 key of the uploaded photo")
    message: str = Field(default="Photo uploaded successfully")


class PhotoDeleteResponse(BaseModel):
    """Response model for photo deletion."""

    message: str = Field(default="Photo deleted successfully")


class PhotosUpdateResponse(BaseModel):
    """Response model for updating user photos list."""

    pictures: list[str] = Field(..., description="Updated list of photo URLs")
    message: str = Field(default="Photos updated successfully")

