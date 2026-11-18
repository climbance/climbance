from climb.mutant_diagnoses.table import mutant_diagnoses
from climb.schema import MutantDiagnosis
from climb.storage import Database, Log


class MutantDiagnosisLog(Log[MutantDiagnosis]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, mutant_diagnoses, MutantDiagnosis)
