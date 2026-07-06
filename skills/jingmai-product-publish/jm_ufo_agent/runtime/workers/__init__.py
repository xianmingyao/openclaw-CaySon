"""运行时 worker 集合。"""

from __future__ import annotations

from jm_ufo_agent.runtime.workers.data_fetch import DataFetchJob, DataFetchWorker
from jm_ufo_agent.runtime.workers.gui_loop import GuiJob, GuiWorker
from jm_ufo_agent.runtime.workers.image_process import ImageProcessJob, ImageProcessWorker

__all__ = ["DataFetchJob", "DataFetchWorker", "GuiJob", "GuiWorker", "ImageProcessJob", "ImageProcessWorker"]
