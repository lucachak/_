import os
import glob
import shutil

def clean_project():
    print("🧹 Iniciando limpeza profunda do projeto Django...")
    
    # 1. Remove o banco de dados
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("✅ Banco de dados db.sqlite3 removido.")
    else:
        print("ℹ️  Nenhum db.sqlite3 encontrado.")

    # 2. Lista de apps para limpar migrations
    # (Adicionei todos que criamos)
    apps = ['Accounts', 'Assets', 'Billing', 'Clients', 'Common', 'Orders', 'Core']
    
    for app in apps:
        migrations_path = os.path.join(app, 'migrations')
        if os.path.exists(migrations_path):
            # Pega todos os arquivos .py dentro da pasta migrations
            files = glob.glob(os.path.join(migrations_path, "*.py"))
            for f in files:
                # NÃO deleta o __init__.py
                if not f.endswith("__init__.py"):
                    os.remove(f)
                    print(f"   🗑️  Removido: {f}")
            
            # Remove cache (__pycache__)
            pycache = os.path.join(migrations_path, "__pycache__")
            if os.path.exists(pycache):
                shutil.rmtree(pycache)
                
    print("\n✨ Limpeza concluída! Agora o ambiente está zerado.")
    print("🚀 Próximos passos:")
    print("1. python manage.py makemigrations Accounts Common")
    print("2. python manage.py makemigrations")
    print("3. python manage.py migrate")
    print("4. python manage.py createsuperuser")

if __name__ == "__main__":
    clean_project()
