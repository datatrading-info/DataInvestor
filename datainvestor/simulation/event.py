class SimulationEvent(object):
    """
    Memorizza un timestamp e una stringa del tipo di evento
    associata a un evento di simulazione.

    Parameters
    ----------
    ts : `pd.Timestamp`
        Il timestamp dell'evento di simulazione.
    event_type : `str`
        La stringa del tipo di evento.
    """

    def __init__(self, ts, event_type):
        self.ts = ts
        self.event_type = event_type

    def __eq__(self, rhs):
        """
        Due entità SimulationEvent sono uguali se condividono
        lo stesso timestamp e tipo di evento.

        Parameters
        ----------
        rhs : `SimulationEvent`
            Il confronto SimulationEvent.

        Returns
        -------
        `boolean`
            Se i due SimulationEvents sono uguali.
        """
        if self.ts != rhs.ts:
            return False
        if self.event_type != rhs.event_type:
            return False
        return True
