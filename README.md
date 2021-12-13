# epubToWeb

Converte um arquivo epub para web book local.

![an example](https://user-images.githubusercontent.com/30227872/113874322-0fba1100-978c-11eb-87e8-16a2a0e3f6b5.png)

#### Requisitos
- Python 2 or 3
- Pip

# TODO
## [ ] Remover iframe. O html de cada capítulo será mostrado diretamente
## [ ] Salvar do localStorage o estado do livro (capitulo, local do scroll, width, fontSize, theme)
## [ ] Limpar código talvez preguiça

#### Como funciona

Se certifique que as dependências foram instaladas:
```commandline
pip install -r requirements.txt
```

Para gerar o web book, execute o comando:
```commandline
python epubToWeb [-h] ARQUIVO.epub DIRETÓRIO_DO_WEB_BOOK
```

Os arquivos serão gerados no diretório indicado no comando.


#### Arquivos gerados
- `book.html`: o arquivo que tu vai abrir no broswer. tem um iframe com teu livro
- `bookIndex.html`: indice dos arquivos (lista de links). o arquivo que vai ta no iframe
- `bookContent/`: os arquivos do epub
- `extractedEpub/`: pasta aonde o conteudo do arquivo foi extraido


---

### [eng]

Converts an epub file to a local web book.

![an example](https://user-images.githubusercontent.com/30227872/113874322-0fba1100-978c-11eb-87e8-16a2a0e3f6b5.png)

#### Requirements
- Python 2 or 3
- Pip

#### How it works

Make sure you have all dependencies installed:

```commandline
pip install -r requirements.txt
```

To generate the web book, run the command:
```commandline
python epubToWeb [-h] FILE.epub WEB_BOOK_FOLDER

```

The web book files will be generated in the specified folder/directory.

#### Generated files
- `book.html`: The file you'll open in your browser. it contains an iframe with the book on it
- `bookIndex.html`: A list with links to the epub content
- `bookContent/`: The folder which contains the epub files
- `extractedEpub/`: The folder where the epub was extracted. It can be deleted
