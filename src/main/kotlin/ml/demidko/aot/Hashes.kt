package ml.demidko.aot


/**
 * Оптимизация
 */
internal object Hashes {
  /**
   * @param zipped результат минификации
   * @return Словарь: хеш -> индексы лемм из списка (коллизии надо проверять)
   */
  fun calculate(zipped: ZipResult): Map<Int, MutableSet<Int>> {
    val res = HashMap<Int, MutableSet<Int>>()
    for (i in zipped.lemmas.indices) {
      val currLemma = zipped.lemmas[i]
      for (flexion in currLemma) {
        res.computeIfAbsent( // хеш флексии
          zipped.strings[flexion.stringIndex].hashCode()
        )  // индекс минифицированной леммы
        { k: Int? -> HashSet() }.add(i)
      }
    }
    return res
  }
}