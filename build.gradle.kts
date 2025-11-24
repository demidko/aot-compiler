repositories {
  mavenCentral()
  maven("https://jitpack.io")
}
plugins {
  kotlin("jvm") version "2.3.0-RC"
  id("com.gradleup.shadow") version "9.2.2"
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
