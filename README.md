# Bataille navale — V2

Jeu terminal Python : joueur humain contre ordinateur, cinq classes séparées.

## Démarrer

Depuis le dossier du projet :

```bash
python -m pip install -e .
bataille-navalle
```

Ou sans installation (macOS/Linux) :

```bash
PYTHONPATH=src python -c 'from bataille_navalle import main; main()'
```

Windows PowerShell :

```powershell
$env:PYTHONPATH='src'
python -c "from bataille_navalle import main; main()"
```

## Contrôles

Coordonnées : `A0`, `C5`, `J9` ; orientation `H` ou `V`.
Les bateaux ne peuvent pas se chevaucher. La flotte contient les tailles 5, 4, 3, 3 et 2.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Notes

L'IA garde ses touches non résolues et attaque en priorité les cases voisines. Quand deux navires se touchent, la seule réponse « Coulé » ne permet pas toujours d'identifier sans ambiguïté toutes les cases du navire détruit : l'IA reste prudente et peut explorer des cases supplémentaires.
