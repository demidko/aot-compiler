package ml.demidko.aot

import java.util.*


/**
 * Класс инкапсулирует способы создания
 */
internal object FlexionFabric {
  /**
   * Конструирование из готового набора
   */
  private fun createFlexion(prefix: String?, base: String, postfix: String, tags: List<MorphologyTag>): FullFlexion {
    val sourceBuilder = StringBuilder()
    if (prefix != null) {
      sourceBuilder.append(prefix)
    }
    if (base[0] != '#') {
      sourceBuilder.append(base)
    }
    return FullFlexion(sourceBuilder.append(postfix).toString(), tags.toSet())
  }

  private fun normalize(token: String): String {
    return token.lowercase(Locale.getDefault()).replace('ё', 'е')
  }

  /**
   * Разбор кода из словаря
   */
  private fun createFlexion(base: String, source: String, morphMap: Map<String, List<MorphologyTag>>): FullFlexion {
    val args = source.split(Regex("\\*")).toTypedArray()
    return createFlexion(
      if (args.size == 2) null else normalize(args[2]),
      normalize(base),
      normalize(args[0]),
      morphMap[args[1]]!!
    )
  }

  /**
   * @param base     база
   * @param paradigm парадигма склонения
   * @param morphMap морфологический словарь
   * @return лемма (содержит флексии, первая флексия собственно лемма остальных)
   */
  fun createLemma(base: String, paradigm: String, morphMap: Map<String, List<MorphologyTag>>): List<FullFlexion> {
    return paradigm.split("%")
      .filter { s: String -> !s.isBlank() }
      .map { src: String ->
        createFlexion(
          base,
          src,
          morphMap
        )
      }
  }
}