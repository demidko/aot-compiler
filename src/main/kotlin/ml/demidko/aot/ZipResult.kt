package ml.demidko.aot

/**
 * Результат сжатия набора лемм
 */
internal class ZipResult(
  val lemmas: List<List<MiniFlexion>>,
  val strings: List<String>,
  val morph: List<Set<MorphologyTag>>
)