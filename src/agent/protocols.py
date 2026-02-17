from src.datatypes import TriageStatus

class WHOIMCIProtocol:
    """
    Centralized repository for WHO IMCI clinical protocols and messaging.
    Ensures consistency between diagnostic reasoning and action plans.
    """
    
    # Standard Clinical Action Recommendations per PRD/WHO Guidelines
    ACTIONS = {
        TriageStatus.RED: "Emergency Danger Signs Detected. Immediate referral.",
        TriageStatus.YELLOW: "Administer oral Amoxicillin. Follow up in 48 hours.",
        TriageStatus.GREEN: "Soothe throat, fluids, rest. No antibiotics needed.",
        TriageStatus.INCONCLUSIVE: "Action: Re-record cough audio ensuring the patient is close to the microphone and background noise is minimized."
    }

    @staticmethod
    def get_action(status: TriageStatus) -> str:
        """
        Map a triage status to the standard WHO IMCI action recommendation.
        """
        return WHOIMCIProtocol.ACTIONS.get(status, "Action plan currently unavailable for this status.")
