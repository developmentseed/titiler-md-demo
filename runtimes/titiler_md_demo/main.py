"""app."""

import re

import jinja2
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette_cramjam.middleware import CompressionMiddleware
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from titiler.core.factory import AlgorithmFactory, ColorMapFactory, TMSFactory
from titiler.core.middleware import CacheControlMiddleware
from titiler.xarray.extensions import VariablesExtension
from titiler.xarray.factory import TilerFactory

from .extensions import DimsExtension
from .settings import ApiSettings

api_settings = ApiSettings()

jinja2_env = jinja2.Environment(
    loader=jinja2.ChoiceLoader([jinja2.PackageLoader(__package__, "templates")])
)
templates = Jinja2Templates(env=jinja2_env)


app = FastAPI(
    title="TiTiler with support of Multidimensional dataset",
    openapi_url="/api",
    docs_url="/api.html",
    version="0.1.0",
    root_path=api_settings.root_path,
)


md = TilerFactory(
    router_prefix="/md",
    extensions=[
        VariablesExtension(),
        DimsExtension(),
    ],
)
app.include_router(md.router, prefix="/md", tags=["Multi Dimensional"])

# TileMatrixSets endpoints
app.include_router(TMSFactory().router, tags=["Tiling Schemes"])

###############################################################################
# Algorithms endpoints
app.include_router(
    AlgorithmFactory().router,
    tags=["Algorithms"],
)

# Colormaps endpoints
app.include_router(
    ColorMapFactory().router,
    tags=["ColorMaps"],
)

add_exception_handlers(app, DEFAULT_STATUS_CODES)

# Set all CORS enabled origins
if api_settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=api_settings.cors_allow_methods,
        allow_headers=["*"],
    )

app.add_middleware(
    CompressionMiddleware,
    minimum_size=0,
    exclude_mediatype={
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/jp2",
        "image/webp",
    },
    compression_level=6,
)

app.add_middleware(
    CacheControlMiddleware,
    cachecontrol=api_settings.cachecontrol,
    exclude_path={r"/healthz"},
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing(request: Request):
    """TiTiler landing page."""
    data = {
        "title": "titiler",
        "demos": [],
        "links": [
            {
                "title": "Landing page",
                "href": str(request.url_for("landing")),
                "type": "text/html",
                "rel": "self",
            },
            {
                "title": "the API definition (JSON)",
                "href": str(request.url_for("openapi")),
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "rel": "service-desc",
            },
            {
                "title": "the API documentation",
                "href": str(request.url_for("swagger_ui_html")),
                "type": "text/html",
                "rel": "service-doc",
            },
            {
                "title": "TiTiler Documentation (external link)",
                "href": "https://developmentseed.org/titiler/",
                "type": "text/html",
                "rel": "doc",
            },
            {
                "title": "TiTiler.Xarray source code (external link)",
                "href": "https://github.com/developmentseed/titiler/tree/main/src/titiler/xarray",
                "type": "text/html",
                "rel": "doc",
            },
        ],
    }

    urlpath = request.url.path
    if root_path := request.app.root_path:
        urlpath = re.sub(r"^" + root_path, "", urlpath)
    crumbs = []
    baseurl = str(request.base_url).rstrip("/")

    crumbpath = str(baseurl)
    for crumb in urlpath.split("/"):
        crumbpath = crumbpath.rstrip("/")
        part = crumb
        if part is None or part == "":
            part = "Home"
        crumbpath += f"/{crumb}"
        crumbs.append({"url": crumbpath.rstrip("/"), "part": part.capitalize()})

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "response": data,
            "template": {
                "api_root": baseurl,
                "params": request.query_params,
                "title": "TiTiler",
            },
            "crumbs": crumbs,
            "url": str(request.url),
            "baseurl": baseurl,
            "urlpath": str(request.url.path),
            "urlparams": str(request.url.query),
        },
    )
