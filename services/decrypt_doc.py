from services.encryption_service import decrypt_value
from config import Config

def decrypt_patient_doc(doc):
    output = dict(doc)
    for field in Config.MEDICAL_FIELDS:
        if field in doc and doc[field] is not None:
            try:
                output[field] = decrypt_value(doc[field])
                # cast back to original numeric
                if field in ["hypertension", "heart_disease", "stroke"]:
                    try:
                        output[field] = int(output[field])
                    except Exception:
                        pass
                # cast back to original float
                elif field in ["bmi", "avg_glucose_level"]:
                    try:
                        output[field] = float(output[field])
                    except Exception:
                        pass
            except Exception:
                output[field] = None
    return output
