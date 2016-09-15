# Crysher - Encryption & Decryption tool

Crysher est un outil en Python de chiffrage et de déchiffrage qui utilise le chiffrement AES-256, compatible avec openssl aes-256-cbc.

### Prerequisities

* Python2.7
* Crypto

```
pip install Crypto
```

## Getting Started

```
$ python crysher.py

usage: crysher.py [-h] [-d] [-e] [-i INPUT] [-m MSGDGST] [-o OUTPUT]
                  [-p PASSPHRASE] [-t TEST] [-v] [-V]
```

Exemple pour chiffrer un fichier:

```
$ python crysher.py -e -i input_file -o output_file
```

Exemple pour déchiffrer un fichier:

```
$ python crysher.py -d -i input_file -o output_file
```

Differentes option sont disponibles:
* -p PASSPHRASE             defini un password
* -m MSGDGST                defini un algorithme de Hashage
* -v                        mode verbose

## Running the tests

Lance une serie de cycle qui genere un password aleatoire entre 8-32 characteres et un text aleatoire entre 20-256 characteres.
Le test consiste a chiffré et déchiffré des données aleatoires, et de comparer les résultats pour etre sure que tout fonctionne correctement.

Le résultat du test ressemble à cela:
```
(2000 / 2000) 100.00%  15 139 2000    0 md5
$ ^      ^     ^        ^  ^   ^      ^ ^- hashage
$ |      |     |        |  |   |      +--- nbr failed
$ |      |     |        |  |   +---------- nbr passed
$ |      |     |        |  +-------------- taille du fichier pour le test
$ |      |     |        +----------------- taille du password pour le test
$ |      |     +-------------------------- poucentage completé
$ |      +-------------------------------- total
$ +--------------------------------------- id du test

```

Exemple de test:

```
python crysher.py -t 2000
```

## Deployment

Crysher est compatible sur:

- Linux

## Authors

* **AneoPsy** - *Initial work*

## Acknowledgments

* Cryptographie
* Python
