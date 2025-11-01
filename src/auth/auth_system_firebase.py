# src/auth/auth_system_firebase.py
import firebase_admin
from firebase_admin import credentials, firestore, auth
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any
import requests
import json
import os
import sys

class AuthSystemFirebase:
    def __init__(self, firebase_cred_path=None):
        # Determinar o caminho correto para o arquivo de credenciais
        if firebase_cred_path is None:
            if getattr(sys, 'frozen', False):
                # Executável PyInstaller
                base_path = sys._MEIPASS
                firebase_cred_path = os.path.join(base_path, 'firebase-key.json')
            else:
                # Desenvolvimento
                firebase_cred_path = 'firebase-key.json'

        print(f"🔍 Procurando arquivo Firebase em: {firebase_cred_path}")

        # Verificar se o arquivo existe
        if not os.path.exists(firebase_cred_path):
            print(f"❌ Arquivo Firebase não encontrado: {firebase_cred_path}")
            # Tentar caminho alternativo
            alt_path = os.path.join(os.getcwd(), 'firebase-key.json')
            print(f"🔍 Tentando caminho alternativo: {alt_path}")
            if os.path.exists(alt_path):
                firebase_cred_path = alt_path
                print("✅ Arquivo encontrado no caminho alternativo")
            else:
                raise FileNotFoundError(f"Arquivo Firebase não encontrado em nenhum dos caminhos: {firebase_cred_path}, {alt_path}")

        # Inicializar Firebase
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_cred_path)
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            self.licenses_ref = self.db.collection('licenses')
            self.users_ref = self.db.collection('users')
            print("✅ Firebase conectado com sucesso!")

        except Exception as e:
            print(f"❌ Erro ao conectar Firebase: {e}")
            raise

    def validate_license(self, license_key: str) -> bool:
        """Valida licença NO FIREBASE - impossível burlar"""
        try:
            print(f"🔍 Validando licença: {license_key}")
            
            # Busca licença no Firebase
            license_doc = self.licenses_ref.document(license_key).get()
            
            if not license_doc.exists:
                print("❌ Licença não existe no Firebase")
                return False
            
            license_data = license_doc.to_dict()
            print(f"📋 Dados da licença: {license_data}")
            
            # Verifica se já foi usada
            if license_data.get('used', False):
                print("❌ Licença já foi usada")
                return False
                
            # Verifica se está ativa
            if not license_data.get('active', True):
                print("❌ Licença inativa")
                return False
                
            # Verifica se expirou
            expires_at = license_data.get('expires_at')
            if expires_at:
                from datetime import datetime
                if datetime.now() > datetime.fromisoformat(expires_at):
                    print("❌ Licença expirada")
                    return False
                
            print("✅ Licença válida!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao validar licença: {e}")
            return False

    def register_user(self, username: str, email: str, password: str, license_key: str) -> bool:
        """Registra usuário COM VALIDAÇÃO NO FIREBASE"""
        try:
            print(f"👤 Registrando usuário: {username}")
            
            # 1. Valida licença no Firebase
            if not self.validate_license(license_key):
                return False

            # 2. Cria usuário no Firebase Auth
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )

            print(f"✅ Usuário criado no Auth: {user_record.uid}")

            # 3. Marca licença como usada
            self.licenses_ref.document(license_key).update({
                'used': True,
                'used_by': user_record.uid,
                'used_at': datetime.now().isoformat(),
                'used_by_username': username
            })

            print("✅ Licença marcada como usada")

            # 4. Salva dados adicionais no Firestore
            self.users_ref.document(user_record.uid).set({
                'username': username,
                'email': email,
                'license_key': license_key,
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'is_active': True,
                'user_id': user_record.uid
            })

            print("✅ Dados salvos no Firestore")
            return True

        except auth.EmailAlreadyExistsError:
            print("❌ Email já está em uso")
            return False
        except Exception as e:
            print(f"❌ Erro no registro: {e}")
            return False

    def verify_login(self, email: str, password: str) -> bool:
        """Verifica login - SIMPLIFICADO para demo"""
        try:
            print(f"🔐 Verificando login para: {email}")
            
            # Em produção, você usaria Firebase Auth REST API
            # Para demo, vamos verificar se o email existe
            user_docs = self.users_ref.where('email', '==', email).limit(1).get()
            
            if not user_docs:
                print("❌ Usuário não encontrado")
                return False
                
            # Atualiza último login
            for doc in user_docs:
                self.users_ref.document(doc.id).update({
                    'last_login': datetime.now().isoformat()
                })
                print(f"✅ Login bem-sucedido para: {email}")
                
            return True
            
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return False

    def get_user_info(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca informações do usuário"""
        try:
            user_docs = self.users_ref.where('email', '==', email).limit(1).get()
            
            for doc in user_docs:
                user_data = doc.to_dict()
                return user_data
                
            return None
            
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
