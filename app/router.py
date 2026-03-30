"""Application configuration - root APIRouter.

Defines all FastAPI application endpoints.

Resources:
    1. https://fastapi.tiangolo.com/tutorial/bigger-applications

"""

from fastapi import APIRouter

from app.controllers.v1 import llm, video, system_controller, plugin_controller, config_controller, template_controller, batch_controller, schedule_controller, analytics_controller, input_controller, publisher_controller

root_api_router = APIRouter()
# v1
root_api_router.include_router(video.router)
root_api_router.include_router(llm.router)
root_api_router.include_router(system_controller.router)
root_api_router.include_router(plugin_controller.router)
root_api_router.include_router(config_controller.router)
root_api_router.include_router(template_controller.router)
root_api_router.include_router(batch_controller.router)
root_api_router.include_router(schedule_controller.router)
root_api_router.include_router(analytics_controller.router)
root_api_router.include_router(input_controller.router)
root_api_router.include_router(publisher_controller.router)
