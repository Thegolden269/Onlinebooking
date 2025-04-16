# Système de Réservation en Ligne

Un système de réservation en ligne permettant aux utilisateurs de réserver des créneaux horaires pour des services spécifiques. Ce projet permet aux utilisateurs de voir les créneaux disponibles, de réserver un créneau et d'annuler leur réservation jusqu'à 4 heures avant l'heure de début.

## 🚀 Fonctionnalités

- **Affichage des créneaux disponibles** : Permet à l'utilisateur de consulter les créneaux horaires disponibles pour une date donnée.
- **Réservation d'un créneau** : Les utilisateurs peuvent réserver un créneau disponible avec leurs informations personnelles.
- **Annulation de réservation** : Les utilisateurs peuvent annuler leur réservation, mais seulement jusqu'à 4 heures avant l'heure de début.
- **Gestion des créneaux** : Les créneaux sont créés automatiquement chaque jour avec des horaires prédéfinis (par exemple, de 9h à 17h).

## 🛠️ Technologies

Ce projet utilise les technologies suivantes :
- **Backend** : Django (Python)
- **Framework API** : Django REST Framework
- **Base de données** : SQLite (ou PostgreSQL, MySQL selon la configuration)
- **Gestion des emails** : Envoi d'emails via un serveur SMTP (ex. Gmail, Mailgun)
- **CORS** : Gestion des origines avec `django-cors-headers`

## 📦 Installation
