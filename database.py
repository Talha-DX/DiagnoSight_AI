import pyodbc
import hashlib
import os
from datetime import datetime


class Database:
    def __init__(self):
        self.db_path = r".\assets\database\DiagnoSightai.accdb"
        self.conn_str = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            rf"DBQ={self.db_path};"
        )
        
        # Create reports directory if it doesn't exist
        self.reports_dir = r"assets\reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def connect(self):
        return pyodbc.connect(self.conn_str)

    # ==================================================
    #                    SECURITY
    # ==================================================
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # ==================================================
    #                    SIGNUP
    # ==================================================
    def create_user(self, username, email, password):
        hashed_pw = self.hash_password(password)
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM users WHERE email = ?", (email,))
                if cur.fetchone():
                    return False, "Email already registered"

                cur.execute(
                    "INSERT INTO users ([username], [email], [password_hash]) VALUES (?, ?, ?)",
                    (username, email, hashed_pw)
                )
                conn.commit()
                return True, "Account created successfully"
        except Exception as e:
            return False, str(e)

    # ==================================================
    #                    LOGIN
    # ==================================================
    def verify_user(self, email, password):
        hashed_pw = self.hash_password(password)
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT [user_id], [username], [email] FROM users WHERE [email] = ? AND [password_hash] = ?",
                    (email, hashed_pw)
                )
                row = cur.fetchone()
                if row:
                    return True, {"user_id": row[0], "username": row[1], "email": row[2]}
                else:
                    return False, "Invalid email or password"
        except Exception as e:
            return False, str(e)

    # ==================================================
    #              DOCTORS (WEB INSIGHTS)
    # ==================================================
    def get_all_doctors(self):
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT [DoctorName],[Specialization],[DiseaseName],[HospitalName],[City],[ExperienceYears],[ContactNumber],[ConsultationFee],[Availability] FROM Doctors"
            )
            rows = cur.fetchall()
            doctors = []
            for row in rows:
                doctors.append({
                    "name": row[0],
                    "specialization": row[1],
                    "disease": row[2],
                    "hospital": row[3],
                    "city": row[4],
                    "experience": row[5],
                    "contact": row[6],
                    "fee": row[7],
                    "availability": row[8]
                })
            return doctors

    # ==================================================
    #              DOCTORS BY DISEASE
    # ==================================================
    def get_doctors_by_disease(self, disease_name, limit=3):
        """Get top doctors specialized in a specific disease"""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                # Access-compatible query - use TOP directly
                query = f"""
                    SELECT TOP {limit} 
                        [DoctorName], [Specialization], [DiseaseName], 
                        [HospitalName], [City], [ExperienceYears], 
                        [ContactNumber], [ConsultationFee], [Availability]
                    FROM Doctors 
                    WHERE [DiseaseName] LIKE ?
                    ORDER BY [ExperienceYears] DESC
                """
                cur.execute(query, (f"%{disease_name}%",))
                
                rows = cur.fetchall()
                doctors = []
                for row in rows:
                    doctors.append({
                        "name": row[0] if row[0] else "N/A",
                        "specialization": row[1] if row[1] else "N/A",
                        "disease": row[2] if row[2] else "N/A",
                        "hospital": row[3] if row[3] else "N/A",
                        "city": row[4] if row[4] else "N/A",
                        "experience": row[5] if row[5] else 0,
                        "contact": row[6] if row[6] else "N/A",
                        "fee": row[7] if row[7] else "Rs N/A",
                        "availability": row[8] if row[8] else "N/A"
                    })
                return doctors
                
        except Exception as e:
            print(f"Error fetching doctors by disease: {e}")
            return []
    

    # ==================================================
    #               UPDATE USER INFO
    # ==================================================
    def update_username(self, user_id, new_username):
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_username, user_id))
                conn.commit()
            return True, "Username updated successfully"
        except Exception as e:
            return False, str(e)

    def update_password(self, user_id, new_password):
        hashed_pw = self.hash_password(new_password)
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (hashed_pw, user_id))
                conn.commit()
            return True, "Password updated successfully"
        except Exception as e:
            return False, str(e)

    def delete_account(self, user_id):
        """Delete user account and all their reports (cascade delete)"""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                # First, delete all reports for this user
                cur.execute("DELETE FROM reports WHERE [user_id] = ?", (user_id,))
                # Then delete the user
                cur.execute("DELETE FROM users WHERE [user_id] = ?", (user_id,))
                conn.commit()
            return True, "Account and all reports deleted successfully"
        except Exception as e:
            return False, str(e)

    # ==================================================
    #               REPORT MANAGEMENT
    # ==================================================
    def save_report(self, user_id, username, prediction_data, image_path=""):
        """Save diagnosis report to database"""
        try:
            # Extract data from prediction
            disease_name = prediction_data.get("predicted_disease", "Unknown")
            confidence = prediction_data.get("confidence", 0)
            severity = prediction_data.get("severity", "Unknown")
            description = prediction_data.get("description", "")
            symptoms = " | ".join(prediction_data.get("symptoms", []))
            treatment = " | ".join(prediction_data.get("treatment", []))
            causes = " | ".join(prediction_data.get("causes", []))
            prevention = " | ".join(prediction_data.get("prevention", []))
            when_to_see_doctor = " | ".join(prediction_data.get("when_to_see_doctor", []))
            complications = " | ".join(prediction_data.get("complications", []))
            recommendation = prediction_data.get("recommendation", "")
            specialist = prediction_data.get("specialist", "Dermatologist")
            
            # Get image filename
            image_filename = os.path.basename(image_path) if image_path else ""
            
            # Generate PDF filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"report_{user_id}_{timestamp}.pdf"
            
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO reports (
                        [user_id], [username], [disease_name], [confidence], 
                        [severity], [description], [symptoms], [treatment],
                        [causes], [prevention], [when_to_see_doctor], 
                        [complications], [recommendation], [specialist],
                        [image_filename], [image_path], [analysis_date], [pdf_filename]
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, username, disease_name, confidence,
                    severity, description, symptoms, treatment,
                    causes, prevention, when_to_see_doctor,
                    complications, recommendation, specialist,
                    image_filename, image_path, datetime.now(), pdf_filename
                ))
                conn.commit()
                
                # Get the inserted report ID
                cur.execute("SELECT @@IDENTITY")
                report_id = cur.fetchone()[0]
                
                return True, {
                    "report_id": report_id,
                    "pdf_filename": pdf_filename,
                    "message": "Report saved successfully"
                }
                
        except Exception as e:
            return False, str(e)

    def get_user_reports(self, user_id):
        """Get all reports for a specific user"""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT 
                        [report_id], [disease_name], [confidence], [severity],
                        [analysis_date], [image_filename], [pdf_filename]
                    FROM reports 
                    WHERE [user_id] = ? 
                    ORDER BY [analysis_date] DESC
                """, (user_id,))
                
                rows = cur.fetchall()
                reports = []
                for row in rows:
                    reports.append({
                        "report_id": row[0],
                        "disease_name": row[1],
                        "confidence": float(row[2]) if row[2] else 0,
                        "severity": row[3] if row[3] else "Unknown",
                        "analysis_date": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "",
                        "image_filename": row[5] if row[5] else "",
                        "pdf_filename": row[6] if row[6] else ""
                    })
                return True, reports
        except Exception as e:
            return False, str(e)

    def get_report_details(self, report_id):
        """Get detailed information for a specific report"""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM reports WHERE [report_id] = ?
                """, (report_id,))
                
                row = cur.fetchone()
                if row:
                    # Get column names
                    columns = [column[0] for column in cur.description]
                    
                    # Convert row to dictionary
                    report = {}
                    for i, col in enumerate(columns):
                        report[col] = row[i]
                    
                    # Convert pipe-separated strings back to lists
                    for field in ["symptoms", "treatment", "causes", "prevention", 
                                  "when_to_see_doctor", "complications"]:
                        if report.get(field):
                            report[field] = report[field].split(" | ")
                        else:
                            report[field] = []
                    
                    return True, report
                else:
                    return False, "Report not found"
        except Exception as e:
            return False, str(e)

    def delete_report(self, report_id):
        """Delete a specific report"""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM reports WHERE [report_id] = ?", (report_id,))
                conn.commit()
            return True, "Report deleted successfully"
        except Exception as e:
            return False, str(e)

    def get_reports_count(self, user_id):
        """Get total number of reports for a user"""
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM reports WHERE [user_id] = ?", (user_id,))
                count = cur.fetchone()[0]
                return True, count
        except Exception as e:
            return False, str(e)