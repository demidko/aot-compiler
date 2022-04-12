repositories {
  mavenCentral()
  maven("https://jitpack.io")
}
plugins {
  kotlin("jvm") version "1.5.31"
  id("com.github.johnrengelman.shadow") version "7.1.0"
}
dependencies {
  implementation("com.github.demidko:aot-bytecode:2021.10.26")
}
tasks.test {
  useJUnitPlatform()
}
tasks.shadowJar {
  isZip64 = true
  manifest.attributes("Main-Class" to "ml.demidko.aot.Compiler")
  minimize()
}
tasks.build {
  dependsOn(tasks.shadowJar)
}
