from src.datatypes import TriageStatus
from src.agent.protocols import WHOIMCIProtocol

def test_protocol_get_action_red():
    """RED status should return emergency referral text."""
    action = WHOIMCIProtocol.get_action(TriageStatus.RED)
    assert action == "Emergency Danger Signs Detected. Immediate referral."

def test_protocol_get_action_yellow():
    """YELLOW status should return antibiotic instruction text."""
    action = WHOIMCIProtocol.get_action(TriageStatus.YELLOW)
    assert action == "Administer oral Amoxicillin. Follow up in 48 hours."

def test_protocol_get_action_green():
    """GREEN status should return home care text."""
    action = WHOIMCIProtocol.get_action(TriageStatus.GREEN)
    assert action == "Soothe throat, fluids, rest. No antibiotics needed."

def test_protocol_get_action_inconclusive():
    """INCONCLUSIVE status should return re-record text (fallback/standard)."""
    action = WHOIMCIProtocol.get_action(TriageStatus.INCONCLUSIVE)
    assert "re-record" in action.lower()
