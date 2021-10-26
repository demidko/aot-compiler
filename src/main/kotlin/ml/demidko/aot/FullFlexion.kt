package ml.demidko.aot

import com.github.demidko.aot.bytecode.MorphologyTag

/**
 * Флексия - вариант леммы
 */
internal class FullFlexion(private val source: String, val tags: Set<MorphologyTag>) {
  override fun toString() = source
}