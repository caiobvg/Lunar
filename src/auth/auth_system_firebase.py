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

    def check_user_exists(self, username: str, email: str) -> Dict[str, bool]:
        """Verifica se username ou email já existem"""
        result = {'username_exists': False, 'email_exists': False}

        try:
            # Verifica email no Firebase Auth
            try:
                auth.get_user_by_email(email)
                result['email_exists'] = True
            except auth.UserNotFoundError:
                pass
            except Exception as e:
                print(f"⚠️ Erro ao verificar email: {e}")

            # Verifica username no Firestore
            try:
                user_docs = self.users_ref.where('username', '==', username).limit(1).get()
                if user_docs:
                    result['username_exists'] = True
            except Exception as e:
                print(f"⚠️ Erro ao verificar username: {e}")

        except Exception as e:
            print(f"❌ Erro geral na verificação: {e}")

        return result

    def register_user(self, username: str, email: str, password: str, license_key: str) -> bool:
        """Registra usuário COM VALIDAÇÃO NO FIREBASE - CORRIGIDO"""
        try:
            print(f"👤 Registrando usuário: {username}, email: {email}")

            # 1. Valida licença no Firebase
            if not self.validate_license(license_key):
                print("❌ Licença inválida")
                return False

            # 2. Verifica se email já existe ANTES de tentar criar
            try:
                print(f"🔍 Verificando se email já existe: {email}")
                existing_user = auth.get_user_by_email(email)
                print(f"❌ Email já está em uso: {email}")
                return False
            except auth.UserNotFoundError:
                print("✅ Email disponível")
                pass  # Email não existe, pode continuar
            except Exception as e:
                print(f"⚠️ Erro ao verificar email: {e}")
                # Continua mesmo com erro na verificação

            # 3. Verifica se username já existe no Firestore
            try:
                print(f"🔍 Verificando se username já existe: {username}")
                user_docs = self.users_ref.where('username', '==', username).limit(1).get()
                if user_docs:
                    print(f"❌ Username já está em uso: {username}")
                    return False
                print("✅ Username disponível")
            except Exception as e:
                print(f"⚠️ Erro ao verificar username: {e}")

            # 4. Cria usuário no Firebase Auth
            try:
                print("🚀 Criando usuário no Firebase Auth...")
                user_record = auth.create_user(
                    email=email,
                    password=password,
                    display_name=username
                )
                print(f"✅ Usuário criado no Auth: {user_record.uid}")

                # 5. Marca licença como usada
                print("🏷️ Marcando licença como usada...")
                self.licenses_ref.document(license_key).update({
                    'used': True,
                    'used_by': user_record.uid,
                    'used_at': datetime.now().isoformat(),
                    'used_by_username': username
                })
                print("✅ Licença marcada como usada")

                # 6. Salva dados adicionais no Firestore
                print("💾 Salvando dados no Firestore...")
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
                print("❌ Email já está em uso (durante criação)")
                return False
            except Exception as e:
                print(f"❌ Erro durante criação do usuário: {e}")
                # Tenta limpar usuário criado parcialmente
                try:
                    if 'user_record' in locals():
                        auth.delete_user(user_record.uid)
                        print("🧹 Usuário removido do Auth devido a erro")
                except:
                    pass
                return False

        except Exception as e:
            print(f"❌ Erro crítico no registro: {e}")
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

    def cleanup_test_data(self, email: str, username: str):
        """Remove dados de teste (use com cuidado!)"""
        try:
            # Encontra usuário pelo email
            user = auth.get_user_by_email(email)

            # Remove do Auth
            auth.delete_user(user.uid)
            print(f"✅ Usuário removido do Auth: {user.uid}")

            # Remove do Firestore
            self.users_ref.document(user.uid).delete()
            print(f"✅ Usuário removido do Firestore: {user.uid}")

            # NOTA: Licença não é liberada automaticamente
            print("⚠️ Licença precisa ser resetada manualmente no Firebase")

        except auth.UserNotFoundError:
            print("❌ Usuário não encontrado no Auth")
        except Exception as e:
            print(f"❌ Erro na limpeza: {e}")

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
