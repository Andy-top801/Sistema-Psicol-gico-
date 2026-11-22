package com.example.sigepsi_movil

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val SPEECH_CHANNEL = "com.example.sigepsi_movil/speech"
    private val PERMISSIONS_CHANNEL = "com.example.sigepsi_movil/permissions"

    private val SPEECH_REQUEST_CODE = 1001
    private val AUDIO_PERMISSION_REQUEST_CODE = 1002
    private val CAMERA_PERMISSION_REQUEST_CODE = 1003

    private var pendingSpeechResult: MethodChannel.Result? = null
    private var pendingCameraResult: MethodChannel.Result? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        // 1. Canal de Reconocimiento de Voz (CU25)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, SPEECH_CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "isSupported" -> {
                    val available = SpeechRecognizer.isRecognitionAvailable(this)
                    result.success(available)
                }
                "startListening" -> {
                    if (pendingSpeechResult != null) {
                        result.error("ALREADY_ACTIVE", "Ya hay una sesión de voz activa", null)
                        return@setMethodCallHandler
                    }
                    pendingSpeechResult = result

                    if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                        ActivityCompat.requestPermissions(
                            this,
                            arrayOf(Manifest.permission.RECORD_AUDIO),
                            AUDIO_PERMISSION_REQUEST_CODE
                        )
                    } else {
                        launchSpeechIntent()
                    }
                }
                "stopListening" -> {
                    pendingSpeechResult = null
                    result.success(true)
                }
                else -> result.notImplemented()
            }
        }

        // 2. Canal de Permisos de Cámara y Video (CU13 - Teleconsulta WebRTC)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, PERMISSIONS_CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "checkCameraPermission" -> {
                    val cameraGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
                    val audioGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
                    result.success(cameraGranted && audioGranted)
                }
                "requestCameraPermission" -> {
                    val cameraGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
                    val audioGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED

                    if (cameraGranted && audioGranted) {
                        result.success(true)
                    } else {
                        pendingCameraResult = result
                        val permsToRequest = mutableListOf<String>()
                        if (!cameraGranted) permsToRequest.add(Manifest.permission.CAMERA)
                        if (!audioGranted) permsToRequest.add(Manifest.permission.RECORD_AUDIO)

                        ActivityCompat.requestPermissions(
                            this,
                            permsToRequest.toTypedArray(),
                            CAMERA_PERMISSION_REQUEST_CODE
                        )
                    }
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun launchSpeechIntent() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, "es-ES")
            putExtra(RecognizerIntent.EXTRA_ONLY_RETURN_LANGUAGE_PREFERENCE, "es-ES")
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Di tu consulta clínica para filtrar reportes (ej: citas canceladas de octubre)")
        }
        try {
            startActivityForResult(intent, SPEECH_REQUEST_CODE)
        } catch (e: Exception) {
            val res = pendingSpeechResult
            pendingSpeechResult = null
            res?.error("UNAVAILABLE", "Servicio de voz no disponible: ${e.message}", null)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            AUDIO_PERMISSION_REQUEST_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    launchSpeechIntent()
                } else {
                    val res = pendingSpeechResult
                    pendingSpeechResult = null
                    res?.error("PERMISSION_DENIED", "Permiso de micrófono no otorgado por el usuario", null)
                }
            }
            CAMERA_PERMISSION_REQUEST_CODE -> {
                val res = pendingCameraResult
                pendingCameraResult = null
                val allGranted = grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }
                res?.success(allGranted)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == SPEECH_REQUEST_CODE) {
            val res = pendingSpeechResult
            pendingSpeechResult = null
            if (resultCode == Activity.RESULT_OK && data != null) {
                val matches = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                res?.success(if (!matches.isNullOrEmpty()) matches[0] else "")
            } else {
                res?.success("")
            }
        }
    }
}
