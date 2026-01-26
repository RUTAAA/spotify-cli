## DESCRIPTION

C'est un scipt Python pour interagir avec l'API de Spotify.
J'ai fait ça pour bind des macros à ma manette.
J'ai pas fait tout l'API car flemme + useless mais c'est une bonne base. Bien que le code ne soit ni propre, ni commenté, ni robuste, mais trkl.

## CONFIGURATION

Faut se créer une app (Web API) [ici](https://developer.spotify.com/dashboard).
Après faut remplir `config.py` à partir de la configuration de votre app.

## UTILISATION

Pour toggle play / pause:

```
python main.py play_pause
```

Pour sauvegarder le son en cours de lecture:

```
python main.py save
```

Pour changer le mode de répétition:

```
python main.py repeat
```

Pour toggle le mode de aléatoire:

```
python main.py shuffle
```

Pour monter le volume:

```
python main.py volume_up
```

Pour descendre le volume:

```
python main.py volume_down
```
