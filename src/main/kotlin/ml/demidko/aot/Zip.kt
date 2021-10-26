package ml.demidko.aot

import com.github.demidko.aot.bytecode.MorphologyTag

/**
 * Класс сжимает набор лемм
 */
internal object Zip {
  fun zip(lemmas: List<List<FullFlexion>>): ZipResult {
    val index = UniqueValues()
    val miniLemmas = lemmas.map {
      zip(
        it,
        index
      )
    }
    return ZipResult(miniLemmas, index.strings, index.tags)
  }

  private fun zip(lemma: List<FullFlexion>, index: UniqueValues): List<MiniFlexion> {
    return lemma.map {
      MiniFlexion(
        index.indexOf(it.toString()),
        index.indexOf(it.tags)
      )
    }
  }

  /**
   * Уникальные наборы значений
   */
  private class UniqueValues {
    private val g_opt: MutableMap<Set<MorphologyTag>, Int> = HashMap<Set<MorphologyTag>, Int>()
    private val s_opt: MutableMap<String, Int> = HashMap()
    val strings: MutableList<String> = ArrayList()
    val tags: MutableList<Set<MorphologyTag>> = ArrayList<Set<MorphologyTag>>()

    /**
     * @param newTag морфологические теги
     * @return индекс тегов в тегохранилище
     */
    fun indexOf(newTag: Set<MorphologyTag>): Int {
      val opt = g_opt[newTag]
      if (opt == null) {
        tags.add(newTag)
        g_opt[newTag] = tags.size - 1
        return tags.size - 1
      }
      return opt
    }

    /**
     * @param str строка
     * @return индекс строки в строкохранилище
     */
    fun indexOf(str: String): Int {
      val opt = s_opt[str]
      if (opt == null) {
        strings.add(str)
        s_opt[str] = strings.size - 1
        return strings.size - 1
      }
      return opt
    }
  }
}