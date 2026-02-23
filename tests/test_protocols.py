from src.datatypes import TriageStatus
from src.agent.protocols import WHORespiratoryProtocol

def test_protocol_get_action_red():
    """RED status should return emergency referral text."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.RED)
    assert action == "Emergency Danger Signs Detected. Immediate referral."

def test_protocol_yellow_action_child():
    """YELLOW status for child should return Amoxicillin instruction."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.YELLOW, age_months=18)
    assert "Amoxicillin" in action

def test_protocol_yellow_action_adult():
    """YELLOW status for adult should return clinical evaluation instruction."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.YELLOW, age_months=420)
    assert "clinical evaluation" in action.lower()
    assert "bronchodilator" in action.lower()

def test_protocol_yellow_action_elderly():
    """YELLOW status for elderly should return COPD workup instruction."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.YELLOW, age_months=816)
    assert "COPD" in action
    assert "oxygen saturation" in action.lower()

def test_protocol_get_action_green():
    """GREEN status should return home care text."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.GREEN)
    assert "Soothe throat" in action

def test_protocol_get_action_inconclusive():
    """INCONCLUSIVE status should return re-record text."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.INCONCLUSIVE)
    assert "re-record" in action.lower()

def test_protocol_backward_compat():
    """Verify get_action works without age_months (defaults to pediatric)."""
    action = WHORespiratoryProtocol.get_action(TriageStatus.YELLOW)
    assert "Amoxicillin" in action
