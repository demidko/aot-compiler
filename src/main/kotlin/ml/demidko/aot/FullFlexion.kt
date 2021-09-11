package ml.demidko.aot

/**
 * Флексия - вариант леммы
 */
internal class FullFlexion(private val source: String, val tags: Set<MorphologyTag>) {
  override fun toString() = source
}