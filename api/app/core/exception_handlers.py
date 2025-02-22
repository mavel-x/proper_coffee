from fastapi import FastAPI, HTTPException, status

from app.core.exceptions import AddressNotFoundError, GeocoderUnavailableError, ObjectNotFoundError


async def geocoder_exception_handler(request, exc):
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="The geocoding service is currently unavailable. Please try again later.",
    ) from exc


async def address_not_found_exception_handler(request, exc):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.args[0]) from exc


async def object_not_found_exception_handler(request, exc):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0]) from exc


def register_exception_handlers(app: FastAPI):
    app.exception_handler(GeocoderUnavailableError)(geocoder_exception_handler)
    app.exception_handler(AddressNotFoundError)(address_not_found_exception_handler)
    app.exception_handler(ObjectNotFoundError)(object_not_found_exception_handler)
