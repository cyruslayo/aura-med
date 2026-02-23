from src.datatypes import TriageStatus, is_pediatric, AgeGroup, get_age_group

class WHORespiratoryProtocol:
    """
    Centralized repository for WHO respiratory clinical protocols and messaging.
    Supports age-adaptive triage following IMCI (pediatric) and IMAI (adult) guidelines.
    """
    
    # Standard Clinical Action Recommendations
    # Split by status and age group sensitivity
    ACTIONS_BASE = {
        TriageStatus.RED: "Emergency Danger Signs Detected. Immediate referral.",
        TriageStatus.GREEN: "Soothe throat, fluids, rest. No antibiotics needed.",
        TriageStatus.INCONCLUSIVE: "Action: Re-record cough audio ensuring the patient is close to the microphone and background noise is minimized."
    }

    @staticmethod
    def get_action(status: TriageStatus, age_months: int = 18) -> str:
        """
        Map a triage status back to age-appropriate WHO clinical recommendations.
        
        Args:
            status: TriageStatus result
            age_months: Patient age in months (defaults to 18 for backward compat)
        """
        if status in WHORespiratoryProtocol.ACTIONS_BASE:
            return WHORespiratoryProtocol.ACTIONS_BASE[status]
        
        if status == TriageStatus.YELLOW:
            # Age-adaptive YELLOW (Pneumonia/Respiratory Pathology) actions
            age_group = get_age_group(age_months)
            
            if is_pediatric(age_months):
                return "Administer oral Amoxicillin. Follow up in 48 hours."
            elif age_group == AgeGroup.ADULT:
                return "Refer for clinical evaluation. Consider bronchodilator therapy if wheezing present."
            else: # ELDERLY
                return "Refer for clinical evaluation. Consider COPD/pneumonia workup. Monitor oxygen saturation."
                
        return "Action plan currently unavailable for this status."
