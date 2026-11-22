allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
// CU13 / HU-44: jitsi_meet_flutter_sdk 13.x declara compileSdk 34, pero sus
// dependencias (androidx.media3 1.8) exigen uno más nuevo. Se fuerza solo en ese módulo.
subprojects {
    afterEvaluate {
        if (name == "jitsi_meet_flutter_sdk") {
            extensions.configure<com.android.build.api.dsl.LibraryExtension> { compileSdk = 36 }
        }
    }
}
subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
