# Projet Labyrinthe de NSI

## But du Jeu
Explorez le labyrinthe généré procéduralement et récolter y des objets tout en évitant les monstres.

## Comment Jouer
- 🧭 **Boussole** toujours visible en bas d'écran pointe vers la salle centrale
- 💻 Utilisez l'ordinateur dans la salle centrale pour :
  - Regénérer le labyrinthe
  - Vendre les objets
  - Sauvegarder/charger votre progression
- 👂 Écoutez les bruits de pas afin de déterminer la position des monstres

## Contrôles
| Action | Touche |
|--------|-----------|
| Se déplacer | **ZQSD** |
| Interagir | **E** |
| Courir | **Shift Gauche** |
| Afficher l'inventaire | **I** |

## Jouer au jeu
### Installer les dépendances
#### Au lycée:
``` batch
./install_requirements_lycee.bat
```
#### Sinon
``` batch
./install_requirements.bat
```
### Lancer le jeu
#### Au lycée:
``` powershell
& "V:\V Python 3.7\python.exe" main.py
```
#### Sinon
``` powershell
python3 main.py
```