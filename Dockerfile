# Utiliser une image Python officielle
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install flask pyyaml

# Set the correct timezone

ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Exposer le port 5000 (celui utilisé par Flask)
EXPOSE 5000

# Définir la commande de démarrage
CMD ["python", "app.py"]
