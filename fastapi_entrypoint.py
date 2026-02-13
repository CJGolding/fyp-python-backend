import asyncio
import logging
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend import TimeSensitiveGameManager, UnrestrictedGameManager
from common import init_logger
from common.types import GameManager

init_logger()

LOG: logging.Logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_managers: dict[str, GameManager] = {}
websocket_step_indices: dict[str, int] = {}


class InitRequest(BaseModel):
    mode: Literal["Unrestricted", "Time-Sensitive"]
    teamSize: int = Field(..., ge=1, le=5)
    pNorm: float = Field(..., ge=1, le=10)
    qNorm: float = Field(..., ge=1, le=10)
    fairnessWeight: float = Field(..., gt=0, le=10)
    queueWeight: float = Field(..., gt=0, le=10)
    matchmakingApproach: Literal["Exact", "Approximate"]


class InitResponse(BaseModel):
    mode: Literal["Unrestricted", "Time-Sensitive"]
    sessionId: str
    teamSize: int
    pNorm: float
    qNorm: float
    fairnessWeight: float
    queueWeight: Optional[float] = None
    skillWindow: int


class ManualInsertionRequest(BaseModel):
    sessionId: str
    mode: Literal["Manual"]
    skill: float = Field(..., ge=0, le=5000)


class AutomaticInsertionRequest(BaseModel):
    sessionId: str
    mode: Literal["Automatic"]
    numPlayers: int = Field(..., ge=1, le=100)
    mean: float = Field(..., ge=0, le=5000)
    stdDev: float = Field(..., ge=0, le=1000)


class CreateMatchRequest(BaseModel):
    sessionId: str


class StopRequest(BaseModel):
    sessionId: str


class StopResponse(BaseModel):
    sessionId: str
    queueSize: list[float]
    heapSize: list[float]
    maxWaitTime: list[float]
    minPriority: list[Optional[float]]
    minImbalance: list[float]


@app.post("/init", response_model=InitResponse)
async def initialise_matchmaking(request: InitRequest) -> InitResponse:
    """
    Initialise a matchmaking session with the specified configuration parameters.
    Creates an instance of the appropriate GameManager based on the request and stores it in a dictionary using a unique session ID.
    :param request: InitRequest containing the configuration parameters for the matchmaking session.
    :return: InitResponse containing the session ID and configuration parameters for frontend state management.
    """
    try:
        approximate = request.matchmakingApproach == "Approximate"

        if request.mode == "Time-Sensitive":
            game_manager = TimeSensitiveGameManager(
                team_size=request.teamSize,
                p_norm=request.pNorm,
                q_norm=request.qNorm,
                fairness_weight=request.fairnessWeight,
                queue_weight=request.queueWeight,
                is_recording=True,
                approximate=approximate
            )
        else:
            game_manager = UnrestrictedGameManager(
                team_size=request.teamSize,
                p_norm=request.pNorm,
                q_norm=request.qNorm,
                fairness_weight=request.fairnessWeight,
                is_recording=True,
                approximate=approximate
            )

        parameters = game_manager.get_parameters()
        game_managers[parameters["session_id"]] = game_manager

        return InitResponse(
            mode=request.mode,
            sessionId=parameters["session_id"],
            teamSize=parameters["team_size"],
            pNorm=parameters["p_norm"],
            qNorm=parameters["q_norm"],
            fairnessWeight=parameters["fairness_weight"],
            queueWeight=parameters.get("queue_weight"),
            skillWindow=parameters["skill_window"]
        )


    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialise matchmaking system: {str(e)}")


@app.post("/insert")
async def insert_players(request: ManualInsertionRequest | AutomaticInsertionRequest) -> dict[str, str | int]:
    """
    Insert players manually (single) or automatically (batch) into the matchmaking system based on the request parameters.
    :param request: ManualInsertionRequest for single player insertion or AutomaticInsertionRequest for batch insertion.
    :return: JSON response indicating the status of the insertion operation.
    """
    try:
        if request.sessionId not in game_managers:
            raise HTTPException(status_code=404, detail="Session not found")

        game_manager = game_managers[request.sessionId]

        if request.mode == "Manual":
            thread = game_manager.insert_player_manually_async(int(request.skill))
            await asyncio.to_thread(thread.join)
            return {"status": "completed", "mode": "manual", "sessionId": request.sessionId}
        else:
            thread = game_manager.insert_players_automatically_async(
                request.numPlayers,
                int(request.mean),
                int(request.stdDev)
            )
            await asyncio.to_thread(thread.join)
            return {
                "status": "completed",
                "mode": "automatic",
                "sessionId": request.sessionId,
                "numPlayers": request.numPlayers
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert players: {str(e)}")


@app.post("/create")
async def create_match(request: CreateMatchRequest) -> dict[str, str]:
    """
    Trigger the matchmaking process to create matches based on the current state of the player queue and game heap.
    :param request: CreateMatchRequest containing the session ID for which to create matches.
    :return: JSON response indicating the status of the match creation operation
    """
    try:
        if request.sessionId not in game_managers:
            raise HTTPException(status_code=404, detail="Session not found")

        game_manager = game_managers[request.sessionId]

        thread = game_manager.create_match_async()
        await asyncio.to_thread(thread.join)

        return {"status": "completed", "sessionId": request.sessionId}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create match: {str(e)}")


@app.post("/stop", response_model=StopResponse)
async def stop_session(request: StopRequest) -> StopResponse:
    """
    Stop the matchmaking session and retrieve statistics about the matchmaking process.
    :param request: StopRequest containing the session ID for which to stop the session and retrieve statistics.
    :return: StopResponse containing the session ID and statistics about the matchmaking process.
    """
    try:
        if request.sessionId not in game_managers:
            raise HTTPException(status_code=404, detail="Session not found")

        game_manager = game_managers[request.sessionId]
        game_manager.cancel()

        stats = game_manager.recorder.get_stats()

        del game_managers[request.sessionId]

        return StopResponse(
            sessionId=request.sessionId,
            queueSize=stats["queue_size"],
            heapSize=stats["heap_size"],
            maxWaitTime=stats["max_wait_time"],
            minPriority=stats["min_priority"],
            minImbalance=stats["min_imbalance"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket endpoint for real-time streaming of matchmaking steps to the frontend, improving responsiveness and user experience.
    The endpoint accepts a WebSocket connection, verifies the session ID, and continuously sends new matchmaking steps as they are recorded by the GameManager's Recorder.
    It handles disconnections and errors gracefully, ensuring that resources are cleaned up appropriately when a client disconnects or an error occurs.
    :param websocket: The WebSocket connection for real-time communication with the frontend.
    :param session_id: The unique session ID associated with the GameManager object.
    """
    await websocket.accept()

    if session_id not in game_managers:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return

    game_manager = game_managers[session_id]

    if session_id not in websocket_step_indices:
        websocket_step_indices[session_id] = 0

    LOG.info(f"Connected session '{session_id}' at index '{websocket_step_indices[session_id]}'")

    try:
        all_steps = game_manager.recorder.get_steps()
        if len(all_steps) > 0:
            LOG.info(f"Sending {len(all_steps)} initial steps")
            await websocket.send_json({"steps": all_steps})
            websocket_step_indices[session_id] = len(all_steps)
        else:
            LOG.info("No initial steps to send")

        while True:
            all_steps = game_manager.recorder.get_steps()
            last_sent_index = websocket_step_indices[session_id]

            if len(all_steps) > last_sent_index:
                new_steps = [step for step in all_steps[last_sent_index:]]
                LOG.info(f"Sending {len(new_steps)} new steps")
                await websocket.send_json({"steps": new_steps})
                websocket_step_indices[session_id] = len(all_steps)

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        LOG.warning(f"Disconnected session '{session_id}' at index '{websocket_step_indices.get(session_id)}'")
    except Exception as e:
        LOG.error(f"Error for session '{session_id}': {e}")
        await websocket.close()
    finally:
        if session_id in websocket_step_indices:
            del websocket_step_indices[session_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
