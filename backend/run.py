import logging

from InquirerPy import inquirer

from backend.time_sensitive_game_manager import TimeSensitiveGameManager
from backend.unrestricted_game_manager import UnrestrictedGameManager

LOG: logging.Logger = logging.getLogger(__name__)


def get_matchmaking_options() -> dict:
    return {
        "message": "Select matchmaking mode: ",
        "choices": [
            {"name": "Unrestricted Queue System", "value": UnrestrictedGameManager},
            {"name": "Time-Sensitive Queue System", "value": TimeSensitiveGameManager},
            {"name": "Exit", "value": exit}
        ]
    }


def get_player_insertion_options() -> dict:
    return {
        "message": "Select action: ",
        "choices": [
            # {"name": "Insert Player", "value": "insert_players_manually"},
            {"name": "Insert Players in Bulk", "value": "insert_players_automatically"},
            {"name": "Start Matchmaking", "value": "start_matchmaking"},
            {"name": "View Steps", "value": "view_steps"},
            {"name": "Exit", "value": "exit"}
        ]
    }


def run():
    """Run the matchmaking system via CLI."""
    system = inquirer.select(**get_matchmaking_options()).execute()()

    while True:
        option: str = inquirer.select(**get_player_insertion_options()).execute()
        if option == "insert_players_automatically":
            system.insert_players_automatically()
        elif option == "start_matchmaking":
            system.create_match()
        elif option == "view_steps":
            for index, step in enumerate(system.recorder.get_steps()):
                LOG.info(f"Step {index + 1}: {step}")
        elif option == "exit":
            break

    for stat_name, stat_value in system.recorder.get_stats().items():
        LOG.info(f"{stat_name}: {stat_value}")
    LOG.info(f"Total matches created: {len(system.created_matches)}")
    LOG.info(f"Final player queue size: {len(system.players)}")
