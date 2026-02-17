from src.datatypes import DangerSignException, LowQualityError, LowConfidenceError, EdgeConstraintViolation

class SafetyGuard:
    """
    Electronic Guardrail following WHO IMCI protocols.
    """
    @staticmethod
    def check(vitals: "PatientVitals") -> None:
        """
        Check for general danger signs per WHO IMCI protocols.
        
        Args:
            vitals: PatientVitals object
            
        Raises:
            DangerSignException: If any emergency danger sign is present.
        """
        # H1: Rule-Based Override for Danger Signs
        active_signs = vitals.danger_sign_details
            
        if active_signs:
            signs_str = " and ".join(active_signs.keys())
            raise DangerSignException(f"Emergency Danger Signs Detected! ({signs_str}) Immediate referral required.")
