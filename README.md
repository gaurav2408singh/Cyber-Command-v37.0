Cyber-Command v37.0: Advanced Multi-Layered Secure Data Framework
🛡️ Project Overview
Developed as an M.Sc. Dissertation project at the University of Lucknow, this framework introduces a "Zero-Knowledge" storage protocol for sensitive government data. By integrating Visual Cryptography, Digital Steganography, and AI-driven Biometrics, the system ensures that sensitive records like Aadhaar or PAN cards are never stored in a single, readable format, effectively eliminating "Single Point of Failure" risks in centralized databases.
🚀 Key Features
•	(2, 2) Threshold Visual Cryptography: Fragments data into a "Government Share" and a "Citizen Share" using bitwise XOR logic.
•	Spatial Domain Steganography: Camouflages encrypted shares within high-resolution "Shadow Covers" using LSB substitution.
•	CNN Biometric Gate: Utilizes the VGG-Face model to bind digital records to the physical owner via a live biometric handshake.
•	Digital Forensic Engine: Provides real-time logging and generates automated PDF Forensic Evidence Reports for every interaction.
________________________________________
🛠️ Technical Stack
•	Language: Python 3.12.
•	Mathematics: NumPy (Vectorized matrix operations).
•	Computer Vision: OpenCV-Python.
•	Deep Learning: DeepFace (TensorFlow/Keras backend for VGG-Face).
•	UI Framework: PyQt6 (Cinematic Neon-Dark Interface).
•	Database: SQLite3 (Secure SHA-256 hashed credential ledger).
________________________________________
📦 Installation & Setup
1.	Clone the Repository:
Bash
git clone https://github.com/gaurav2408singh/Cyber-Command-v37.0.git
cd Cyber-Command-v37.0
2.	Create a Virtual Environment:
Bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
3.	Install Dependencies:
Bash
pip install -r requirements.txt
________________________________________
🚦 Execution Guide
1. Running the Final Application
To launch the complete multi-layered dashboard, run the master controller:
Bash
python main.py
•	Phase 0 (Authorization): Login or Register a new official identity.
•	Phase 1 (Enrollment): Upload an ID, link live biometrics, set a passkey, and execute the protocol to generate steganographic shares .
•	Phase 2 (Authentication): Clear the AI biometric barrier (>=40% similarity), enter credentials, and reconstruct the original data .
2. Understanding Individual Modules
If you wish to test or audit specific components of the engine:
•	modules/crypto_engine.py: Contains the logic for generate_color_shares() and reconstruct_color_id(). It performs the (2, 2) XOR split on RGB planes to ensure 100% reconstruction fidelity.
•	modules/stego_engine.py: Handles the embed_lsb() and extract_lsb() functions. It targets the 0th bit-plane to hide data with an imperceptible PSNR of >51 dB.
•	modules/forensic_engine.py: Manages the perform_ai_face_match() using VGG-Face and the generate_forensic_report() function to create the final PDF evidence.
________________________________________
👨‍💻 Developer Information
•	Developer: Gaurav Singh (Roll No: 2410015015007).
•	Institution: Department of Computer Science, University of Lucknow.
•	Research Supervisor: Dr. S.P. Kannojia.
•	Status: M.Sc. IV Semester Dissertation (2025-2026).
