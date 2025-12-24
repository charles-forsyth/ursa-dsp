from pydantic import BaseModel, Field
from enum import Enum


class DataClassification(str, Enum):
    P3 = "P3 (Moderate)"
    P4 = "P4 (High)"
    HIPAA = "HIPAA"
    CUI = "CUI"
    EXPORT_CONTROLLED = "Export Controlled"


class InfrastructureType(str, Enum):
    WORKSTATION = "Standalone Workstation"
    CLUSTER = "UCR Research Cluster"
    CLOUD = "Cloud (AWS/GCP)"
    AIR_GAP = "Air-Gapped Server"


class ProjectMetadata(BaseModel):
    project_name: str = Field(..., description="Official name of the research project")
    pi_name: str = Field(..., description="Principal Investigator Name")
    uisl_name: str = Field(..., description="Unit Information Security Lead Name")
    department: str = Field(..., description="Research Department/Unit")

    classification: DataClassification = Field(
        DataClassification.P4, description="Highest data classification level"
    )
    is_cui: bool = Field(False, description="Does this involve CUI?")
    data_provider: str = Field(..., description="External data provider (e.g., NIH)")

    infrastructure: InfrastructureType = Field(
        InfrastructureType.WORKSTATION, description="Primary storage infrastructure"
    )
    transfer_method: str = Field("Encrypted Drive", description="Data transfer method")
    os_type: str = Field("Linux", description="Operating System")

    retention_date: str = Field(..., description="Project end/retention date")
    destruction_method: str = Field(
        "DoD 5220.22-M", description="Data destruction standard"
    )

    def to_summary_text(self) -> str:
        """Converts metadata into a prose summary for the AI."""
        return f"""
        **Project Identity:**
        Project: {self.project_name}
        PI: {self.pi_name}
        UISL: {self.uisl_name}
        Department: {self.department}

        **Data Sensitivity:**
        Classification: {self.classification.value}
        CUI: {"Yes" if self.is_cui else "No"}
        Data Provider: {self.data_provider}

        **Infrastructure:**
        Type: {self.infrastructure.value}
        OS: {self.os_type}
        Transfer Method: {self.transfer_method}

        **Lifecycle:**
        Retention Date: {self.retention_date}
        Destruction: {self.destruction_method}
        """
