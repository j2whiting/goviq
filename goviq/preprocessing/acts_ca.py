from goviq.preprocessing.parl_ca import ParlCAPreprocessor


class ActCAPreprocessor(ParlCAPreprocessor):
    """Placeholder for now, I suspect these preprocessors will diverge in functionality."""
    def __init__(self, local_cache: str = None):
        super().__init__(local_cache=local_cache)
