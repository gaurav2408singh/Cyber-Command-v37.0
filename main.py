import sys, os, cv2, qrcode, datetime, time, sqlite3, hashlib
import numpy as np 
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QTextEdit, QHBoxLayout, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QTabWidget, QMessageBox, QLineEdit, QFrame, QStackedWidget)
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# Core Logic Imports
from modules.crypto_engine import generate_color_shares, reconstruct_color_id, get_random_cover, verify_integrity
from modules.stego_engine import embed_lsb, extract_lsb
from modules.forensic_engine import perform_ai_face_match, generate_forensic_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# DATABASE & SECURITY
# ============================================================
def init_db():
    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    conn = sqlite3.connect(os.path.join(data_dir, "users.db"))
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)')
    conn.commit(); conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================
# PHASE 0: CINEMATIC LOGIN PORTAL
# ============================================================
class LoginPortal(QWidget):
    login_success = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("University of Lucknow | Secure Access Gate")
        init_db()
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #02040a, stop:0.5 #0d1117, stop:1 #02040a); }")

        self.card = QFrame()
        self.card.setFixedSize(500, 780)
        self.card.setStyleSheet("QFrame { background-color: rgba(13, 17, 23, 230); border: 2px solid #1f6feb; border-radius: 30px; }")
        card_lyt = QVBoxLayout(self.card); card_lyt.setContentsMargins(40, 20, 40, 40); card_lyt.setSpacing(10)

        logo_lbl = QLabel()
        logo_path = os.path.join(BASE_DIR, "lu_logo.png")
        if os.path.exists(logo_path):
            logo_lbl.setPixmap(QPixmap(logo_path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); card_lyt.addWidget(logo_lbl)

        title = QLabel("UNIVERSITY OF LUCKNOW"); title.setStyleSheet("font-size: 24px; font-weight: 900; color: white; border:none; background:transparent;")
        dept = QLabel("Department of Computer Science"); dept.setStyleSheet("font-size: 16px; color: #58a6ff; font-weight: bold; border:none; background:transparent;")
        name = QLabel("Developed by: GAURAV SINGH"); name.setStyleSheet("font-size: 14px; color: #00ff88; font-family: 'Consolas'; border:none; background:transparent;")
        for l in [title, dept, name]: l.setAlignment(Qt.AlignmentFlag.AlignCenter); card_lyt.addWidget(l)

        self.stack = QStackedWidget(); self.stack.addWidget(self.create_login_w()); self.stack.addWidget(self.create_reg_w())
        card_lyt.addWidget(self.stack); self.main_layout.addWidget(self.card)

    def create_login_w(self):
        w = QWidget(); lyt = QVBoxLayout(w); lyt.setSpacing(20)
        self.u_in = QLineEdit(); self.u_in.setPlaceholderText("Username")
        self.p_in = QLineEdit(); self.p_in.setPlaceholderText("Password"); self.p_in.setEchoMode(QLineEdit.EchoMode.Password)
        style = "QLineEdit { background: #010409; color: white; border: 1px solid #30363d; padding: 15px; border-radius: 12px; }"
        self.u_in.setStyleSheet(style); self.p_in.setStyleSheet(style)
        btn = QPushButton("AUTHENTICATE ACCESS"); btn.clicked.connect(self.handle_login)
        btn.setStyleSheet("QPushButton { background: #1f6feb; color: white; height: 50px; font-weight: bold; border-radius: 12px; }")
        sw = QPushButton("New User? Register Identity"); sw.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        sw.setStyleSheet("background: transparent; color: #58a6ff; border: none; text-decoration: underline;")
        lyt.addStretch(); lyt.addWidget(self.u_in); lyt.addWidget(self.p_in); lyt.addWidget(btn); lyt.addWidget(sw); lyt.addStretch()
        return w

    def create_reg_w(self):
        w = QWidget(); lyt = QVBoxLayout(w); lyt.setSpacing(20)
        self.ru_in = QLineEdit(); self.ru_in.setPlaceholderText("New Username")
        self.rp_in = QLineEdit(); self.rp_in.setPlaceholderText("New Password"); self.rp_in.setEchoMode(QLineEdit.EchoMode.Password)
        style = "QLineEdit { background: #010409; color: white; border: 1px solid #30363d; padding: 15px; border-radius: 12px; }"
        self.ru_in.setStyleSheet(style); self.rp_in.setStyleSheet(style)
        btn = QPushButton("REGISTER"); btn.clicked.connect(self.handle_reg)
        btn.setStyleSheet("background: #238636; color: white; height: 50px; font-weight: bold; border-radius: 12px;")
        bk = QPushButton("← Back to Login"); bk.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        bk.setStyleSheet("background: transparent; color: #00f2ff; border: none;")
        lyt.addStretch(); lyt.addWidget(self.ru_in); lyt.addWidget(self.rp_in); lyt.addWidget(btn); lyt.addWidget(bk); lyt.addStretch()
        return w

    def handle_login(self):
        u, p = self.u_in.text().strip(), self.p_in.text().strip()
        if not u or not p: QMessageBox.warning(self, "Input Required", "Enter Username and Password!"); return
        pw_h = hash_password(p); conn = sqlite3.connect(os.path.join(BASE_DIR, "data", "users.db")); cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (u, pw_h))
        if cursor.fetchone(): conn.close(); self.login_success.emit()
        else: QMessageBox.critical(self, "Denied", "Authentication Failed!"); conn.close()

    def handle_reg(self):
        u, p = self.ru_in.text().strip(), self.rp_in.text().strip()
        if not u or not p: QMessageBox.warning(self, "Input Required", "All fields required!"); return
        try:
            pw_h = hash_password(p); conn = sqlite3.connect(os.path.join(BASE_DIR, "data", "users.db")); cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES (?,?)", (u, pw_h)); conn.commit(); conn.close()
            QMessageBox.information(self, "Success", "Registry Updated!"); self.stack.setCurrentIndex(0)
        except: QMessageBox.warning(self, "Error", "Username exists.")

# ============================================================
# MAIN DASHBOARD (PHASE 1 & 2)
# ============================================================
class AIWorker(QThread):
    finished = pyqtSignal(bool, float)
    def __init__(self, target, frame): super().__init__(); self.target, self.frame = target, frame
    def run(self): m, s = perform_ai_face_match(self.target, self.frame); self.finished.emit(m, s)

class CyberAI_Dashboard_V37(QMainWindow):
    def __init__(self, user="Admin"):
        super().__init__()
        self.logged_user = user # For Audit Tracking
        self.setWindowTitle(f"CYBER-COMMAND v37.0 | Official: {user} | Gaurav Singh | LU")
        self.setMinimumSize(1580, 980)
        
        self.id_path = self.session_pass = self.current_otp = self.integrity_seal = None
        self.enroll_verified = self.auth_ai_verified = False 
        self.timer_seconds = 120; self.attempts = 3; self.min_threshold = 40.0; self.current_score = 0.0
        
        self.otp_timer = QTimer(); self.otp_timer.timeout.connect(self.update_countdown)
        self.setup_ui()
        self.log(f"AUTHORIZED LOGIN: SYSTEM ACCESSED BY OFFICIAL [{user.upper()}]")

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #020408; }
            QTabWidget::pane { border: 2px solid #00f2ff; background: #070d14; border-radius: 15px; }
            QTabBar::tab:selected { background: #1f6feb; color: white; padding: 10px 30px; font-weight: bold; }
            QLabel { color: #00f2ff; font-family: 'Consolas'; font-size: 13px; }
            QLineEdit { background: #010409; color: #00ff88; border: 1px solid #1f6feb; padding: 12px; border-radius: 8px; }
            QPushButton { background: #1f6feb; color: white; font-weight: bold; border-radius: 8px; min-height: 45px; }
            QPushButton#ActionBtn { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ff88, stop:1 #1f6feb); color: black; }
            QTextEdit { background: #010409; color: #79c0ff; border: 1px solid #1f6feb; border-radius: 12px; font-family: 'Consolas'; }
        """)
        self.tabs = QTabWidget(); self.setCentralWidget(self.tabs)
        self.tabs.addTab(self.init_enroll_ui(), "PHASE 1: ENROLLMENT")
        self.tabs.addTab(self.init_auth_ui(), "PHASE 2: AUTHENTICATION")

    def create_cell(self, title, color="#1f6feb"):
        frame = QFrame(); frame.setStyleSheet(f"border: 2px solid {color}; border-radius: 15px; background: #0d1117;")
        lyt = QVBoxLayout(); header = QLabel(title.upper()); header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img = QLabel("IDLE"); img.setAlignment(Qt.AlignmentFlag.AlignCenter); img.setFixedSize(300, 250)
        lyt.addWidget(header); lyt.addWidget(img); frame.setLayout(lyt); return frame, img

    def init_enroll_ui(self):
        page = QWidget(); lyt = QGridLayout()
        f1, self.e_orig = self.create_cell("01. ID Source"); f2, self.e_cam = self.create_cell("02. Biometric Link", "#ffcc00")
        f3, self.e_s1 = self.create_cell("03. Govt Share", "#00ff88"); f4, self.e_s2 = self.create_cell("04. Citizen Share", "#bc13fe")
        f5, self.e_cover = self.create_cell("05. Shadow Cover", "#ffcc00"); f6, self.e_stego = self.create_cell("06. Stego Output", "#00ff88")
        f7, self.e_qr = self.create_cell("07. QR Access Key", "#bc13fe")
        lyt.addWidget(f1, 0, 0); lyt.addWidget(f2, 0, 1); lyt.addWidget(f3, 0, 2); lyt.addWidget(f4, 1, 0); lyt.addWidget(f5, 1, 1); lyt.addWidget(f6, 1, 2); lyt.addWidget(f7, 2, 2)
        
        self.audit_log = QTextEdit(); self.audit_log.setReadOnly(True)
        self.otp_display = QLabel("ISSUED OTP: ------")
        self.otp_display.setStyleSheet("font-size: 24px; color: #00ff88; font-weight: bold; background: #010409; padding: 10px; border: 1px solid #00ff88;")
        log_lyt = QVBoxLayout(); log_lyt.addWidget(QLabel("COMMAND AUDIT")); log_lyt.addWidget(self.audit_log); log_lyt.addWidget(self.otp_display)
        lyt.addLayout(log_lyt, 0, 3, 3, 1)
        
        ctrl = QHBoxLayout()
        btn_id = QPushButton("UPLOAD ID"); btn_id.clicked.connect(self.upload_id)
        btn_reg = QPushButton("LINK BIOMETRICS"); btn_reg.clicked.connect(self.enroll_biometric)
        self.p_in = QLineEdit(); self.p_in.setEchoMode(QLineEdit.EchoMode.Password); self.p_in.setPlaceholderText("Set Passkey...")
        btn_exec = QPushButton("EXECUTE PROTOCOL"); btn_exec.setObjectName("ActionBtn"); btn_exec.clicked.connect(self.run_enrollment)
        ctrl.addWidget(btn_id); ctrl.addWidget(btn_reg); ctrl.addWidget(self.p_in); ctrl.addWidget(btn_exec)
        
        self.e_tm = QLabel("OTP STATUS: OFFLINE"); footer = QVBoxLayout(); footer.addLayout(ctrl); footer.addWidget(self.e_tm, alignment=Qt.AlignmentFlag.AlignCenter)
        lyt.addLayout(footer, 3, 0, 1, 4); page.setLayout(lyt); return page

    def init_auth_ui(self):
        page = QWidget(); lyt = QGridLayout()
        self.v_res = QLabel("WAITING"); self.v_res.setFixedSize(600, 450); self.v_res.setStyleSheet("border: 2px solid #bc13fe; border-radius: 20px; background: #010409;")
        self.v_cam = QLabel("LIVE CAMERA"); self.v_cam.setFixedSize(600, 450); self.v_cam.setStyleSheet("border: 2px solid #00f2ff; border-radius: 20px; background: #010409;")
        self.att_lbl = QLabel(f"SECURITY ATTEMPTS: {self.attempts}/3"); self.stat_lbl = QLabel("AI: STANDBY"); self.v_tm = QLabel("TIMER: 02:00")
        v_ctrl = QVBoxLayout(); v_ctrl.setSpacing(10); self.v_p = QLineEdit(); self.v_p.setPlaceholderText("Enter Passkey"); self.v_p.setEchoMode(QLineEdit.EchoMode.Password); self.v_o = QLineEdit(); self.v_o.setPlaceholderText("Enter OTP")
        btn_ai = QPushButton("STAGE 1: SCAN BIOMETRICS"); btn_ai.clicked.connect(self.run_auth_ai)
        btn_dec = QPushButton("STAGE 2: DECRYPT IDENTITY"); btn_dec.clicked.connect(self.run_verification); btn_rep = QPushButton("STAGE 3: FORENSIC REPORT"); btn_rep.clicked.connect(self.run_report)
        v_ctrl.addWidget(self.v_tm); v_ctrl.addWidget(self.att_lbl); v_ctrl.addWidget(btn_ai); v_ctrl.addSpacing(10); v_ctrl.addWidget(QLabel("Passkey:")); v_ctrl.addWidget(self.v_p); v_ctrl.addWidget(QLabel("OTP:")); v_ctrl.addWidget(self.v_o); v_ctrl.addWidget(btn_dec); v_ctrl.addWidget(btn_rep)
        lyt.addWidget(self.v_res, 0, 0); lyt.addWidget(self.v_cam, 0, 1); lyt.addLayout(v_ctrl, 0, 2); lyt.addWidget(self.stat_lbl, 1, 1); page.setLayout(lyt); return page

    # --- ENROLLMENT LOGIC (With User Attribution) ---
    def upload_id(self):
        self.id_path, _ = QFileDialog.getOpenFileName(self, "Open ID")
        if self.id_path: 
            self.display_fit(self.e_orig, QPixmap(self.id_path))
            self.log(f"ACTION: ID Document Loaded by User [{self.logged_user}]")
        else: QMessageBox.warning(self, "Input Missing", "Please select an ID document.")

    def enroll_biometric(self):
        if not self.id_path: 
            QMessageBox.critical(self, "Sequence Error", "Upload ID (Step 1) before Biometric Link!")
            return
        cap = cv2.VideoCapture(0); ret, frame = cap.read(); cap.release()
        if ret:
            self.display_fit(self.e_cam, self.cv_to_pix(frame))
            self.worker = AIWorker(self.id_path, frame); self.worker.finished.connect(self.on_enroll_done); self.worker.start()
            self.log(f"ACTION: Biometric Link Initialized for User [{self.logged_user}]")

    def on_enroll_done(self, m, s):
        if m and s >= self.min_threshold:
            self.enroll_verified = True
            self.log(f"ENROLL SUCCESS: Biometric Match Verified ({s}%). User confirmed.")
            QMessageBox.information(self, "Success", "Identity Linked to Document.")
        else: 
            self.enroll_verified = False
            self.log(f"ENROLL DENIED: Biometric Mismatch ({s}%). Unauthorized entity detected.", True)
            QMessageBox.critical(self, "Security Denial", f"Face Match Score ({s}%) too low.")

    def run_enrollment(self):
        if not self.id_path: QMessageBox.critical(self, "Error", "ID Document missing!"); return
        if not self.enroll_verified: QMessageBox.critical(self, "Barrier", "Biometric link required!"); return
        pw = self.p_in.text().strip()
        if not pw: QMessageBox.warning(self, "Input Required", "Define a Passkey!"); return

        s1, s2, seal, otp = generate_color_shares(self.id_path)
        self.session_pass, self.current_otp, self.integrity_seal = pw, otp, seal
        self.otp_display.setText(f"ISSUED OTP: {otp}")
        
        # AUDIT OTP
        self.log(f"PROTOCOL: Secure Encryption Executed. OTP [{otp}] Issued to User [{self.logged_user}]")

        cover = get_random_cover(); p1 = embed_lsb(s1, cover, os.path.join(BASE_DIR, "data", "stego_shares", "govt_share.png"), pw)
        embed_lsb(s2, cover, os.path.join(BASE_DIR, "data", "stego_shares", "citizen_share.png"), pw)
        qr_img = qrcode.make(otp).convert('RGB'); q_qr = QImage(qr_img.tobytes(), qr_img.width, qr_img.height, qr_img.width*3, QImage.Format.Format_RGB888)
        self.display_fit(self.e_qr, QPixmap.fromImage(q_qr)); self.display_fit(self.e_s1, self.cv_to_pix(s1)); self.display_fit(self.e_s2, self.cv_to_pix(s2)); self.display_fit(self.e_cover, QPixmap(cover)); self.display_fit(self.e_stego, QPixmap(p1))
        self.timer_seconds = 120; self.otp_timer.start(1000)

    # --- AUTHENTICATION LOGIC (Detailed Fail Audit + Timer Stop) ---
    def run_auth_ai(self):
        if not self.current_otp: QMessageBox.critical(self, "Expired", "Session expired."); return
        cap = cv2.VideoCapture(0); ret, frame = cap.read(); cap.release()
        if ret:
            self.display_fit(self.v_cam, self.cv_to_pix(frame))
            self.auth_worker = AIWorker(self.id_path, frame); self.auth_worker.finished.connect(self.on_auth_ai_done); self.auth_worker.start()
            self.log(f"AUTH ACTION: Stage 1 Biometric Scan by User [{self.logged_user}]")

    def on_auth_ai_done(self, m, s):
        self.current_score = s
        if m and s >= self.min_threshold:
            self.auth_ai_verified = True; self.stat_lbl.setText(f"MATCH: {s}%"); self.stat_lbl.setStyleSheet("color: #00ff88;")
            self.log(f"AUTH SUCCESS: Stage 1 Verified ({s}%).")
        else: 
            self.auth_ai_verified = False; self.stat_lbl.setText(f"FAILED: {s}%"); self.stat_lbl.setStyleSheet("color: red;")
            self.log(f"AUTH FAILED: Stage 1 Biometric Mismatch ({s}%).", True)
            QMessageBox.critical(self, "Denied", "Biometric verification failed.")

    def run_verification(self):
        if not self.auth_ai_verified: QMessageBox.critical(self, "Locked", "Pass Stage 1 Biometrics first!"); return
        pw, otp = self.v_p.text().strip(), self.v_o.text().strip()
        if not pw or not otp: QMessageBox.warning(self, "Input Required", "Enter both Passkey and OTP."); return

        if pw == self.session_pass and otp == self.current_otp:
            # STOP TIMER ON SUCCESS
            self.otp_timer.stop() 
            self.log(f"IDENTITY MATCH: User [{self.logged_user}] provided Correct Credentials. MFA COUNTDOWN HALTED.")

            gs = extract_lsb(os.path.join(BASE_DIR, "data", "stego_shares", "govt_share.png"), self.session_pass)
            cs = extract_lsb(os.path.join(BASE_DIR, "data", "stego_shares", "citizen_share.png"), self.session_pass)
            res = reconstruct_color_id(gs, cs); self.display_fit(self.v_res, self.cv_to_pix(res))
            
            if verify_integrity(res, self.integrity_seal): 
                self.log(f"FINAL RESULT: Document Restored. Integrity SHA-256 Validated. Access Granted to [{self.logged_user}].")
            QMessageBox.information(self, "Success", "Decryption Complete. Identity Restored.")
        else:
            self.attempts -= 1; self.att_lbl.setText(f"SECURITY ATTEMPTS: {self.attempts}/3")
            # AUDIT FAILED CREDENTIALS
            self.log(f"SECURITY VIOLATION: User [{self.logged_user}] entered Wrong Credentials. {self.attempts} attempts remaining.", True)
            
            QMessageBox.warning(self, "Access Denied", f"Invalid Credentials! {self.attempts} attempts left.")
            if self.attempts <= 0:
                self.log(f"SYSTEM LOCKOUT: User [{self.logged_user}] triggered brute-force protection.", True)
                QMessageBox.critical(self, "LOCKOUT", "Zero attempts remaining. Closing."); sys.exit()

    def run_report(self):
        if not self.auth_ai_verified: return
        self.log(f"REPORT: User [{self.logged_user}] Exporting Forensic Evidence PDF.")
        path = generate_forensic_report(self.stat_lbl.text(), str(self.current_score), self.audit_log.toPlainText())
        QMessageBox.information(self, "Success", "Forensic Audit Trail Exported.")

    def log(self, msg, is_err=False):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        c = "red" if is_err else "#00f2ff"
        self.audit_log.append(f"<font color='{c}'>[{t}]</font> ▶ {msg}")

    def update_countdown(self):
        self.timer_seconds -= 1; m, s = divmod(max(0, self.timer_seconds), 60)
        self.v_tm.setText(f"TIMER: {m:02d}:{s:02d}"); self.e_tm.setText(f"OTP SESSION: {m:02d}:{s:02d}")
        if self.timer_seconds <= 0:
            self.current_otp = None; self.otp_display.setText("ISSUED OTP: EXPIRED")
            self.log(f"SESSION TIMEOUT: MFA Window for User [{self.logged_user}] has Closed.", True)

    def cv_to_pix(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); h, w, c = rgb.shape
        return QPixmap.fromImage(QImage(rgb.data, w, h, c * w, QImage.Format.Format_RGB888))

    def display_fit(self, label, pix):
        if not pix.isNull(): label.setPixmap(pix.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

# ============================================================
# MASTER CONTROLLER
# ============================================================
class MasterController:
    def __init__(self):
        self.login_window = LoginPortal()
        self.login_window.login_success.connect(self.show_main_app); self.login_window.showFullScreen()
    def show_main_app(self):
        user = self.login_window.u_in.text(); self.main_app = CyberAI_Dashboard_V37(user=user)
        self.main_app.show(); self.login_window.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stego_dir = os.path.join(BASE_DIR, "data", "stego_shares")
    if not os.path.exists(stego_dir): os.makedirs(stego_dir)
    ctrl = MasterController(); sys.exit(app.exec())