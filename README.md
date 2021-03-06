# Aot Compiler

Компилятор [файлов aot-словаря](https://github.com/sokirko74/morph_dict/) [русской морфологии](https://github.com/sokirko74/morph_dict/tree/master/data/Russian)
в оптимизированный для быстрого поиска бинарный формат.

## Исходный текстовый формат

Документация расположена
в [оригинальном репозитории aot](https://github.com/sokirko74/aot/blob/master/Docs/Morph_UNIX.txt).

## Оптимизированный бинарный формат (`mrd.gz`)

```
количество морфологий
морфология
...
морфология 

количество строк
строка
...
строка

количество лемм
(индекс строки, индекс морфологии) (индекс строки, индекс морфологии)... (индекс строки, индекс морфологии) (индекс строки, индекс морфологии)
(индекс строки, индекс морфологии) (индекс строки, индекс морфологии)... (индекс строки, индекс морфологии) (индекс строки, индекс морфологии)
...
(индекс строки, индекс морфологии) (индекс строки, индекс морфологии)... (индекс строки, индекс морфологии) (индекс строки, индекс морфологии)

количество хешей (коллизии проверяются в рантайме, нет смысла отделяеть их во время компиляции, т. к. могут быть и внешние коллизии)
хеш, индекс леммы, индекс леммы
хеш, индекс леммы, индекс леммы, индекс леммы
хеш, индекс леммы, индекс леммы, индекс леммы, индекс леммы
...
хеш, индекс леммы, индекс леммы, индекс леммы
```

## Проверка данных

Для проверки результатов выводится статистика.  
Эталонные результаты компиляции должны быть такие:

```
Compilation [1..4]
1. Morphology (579)
2. Strings (3039129)
3. Lemma indexes (174628)
4. Flexion hashes (3034914)
```

## Build with Java

Execute `./gradlew clean build`. Your jar will be located at `./build/libs` with `-all.jar` postfix. Now you can compile
morphology:

```shell
java -jar aot-binary-all.jar
```

## Or, build with Docker

Execute `docker build . -t aot-binary`. Your image will be located at `docker images -a`. Now you can compile
morphology:

```shell
docker run -v `pwd`:`pwd` -w `pwd` -it --rm aot-binary
```
