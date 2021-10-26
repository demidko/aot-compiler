package ml.demidko.aot

import com.github.demidko.aot.bytecode.MorphologyTag

/**
 * Результат сжатия набора лемм
 */
internal class ZipResult(
  val lemmas: List<List<MiniFlexion>>,
  val strings: List<String>,
  val morph: List<Set<MorphologyTag>>
)