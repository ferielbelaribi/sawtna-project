import 'package:flutter/material.dart';
import 'package:sawtna/Screens/compliance_check_screen.dart';
import 'package:sawtna/Screens/home_screen.dart';
import 'package:sawtna/Screens/image_generation_screen.dart';
import 'package:sawtna/Screens/intro2_screen.dart';
import 'package:sawtna/Screens/intro_screen.dart';
import 'package:sawtna/Screens/login_screen.dart';
import 'package:sawtna/Screens/register_screen.dart';
import 'package:sawtna/Screens/splash_screen.dart';
import 'package:sawtna/Screens/text_generation_screen.dart';
import 'package:sawtna/services/auth_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SAWTNA App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.red,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/intro': (context) => const IntroScreen(),
        '/intro2': (context) => const Intro2Screen(),
        '/login': (context) => const LoginScreen(),
        '/registration': (context) => const RegisterScreen(),
        '/home': (context) => const HomeScreen(),
        '/text_generation': (context) => const TextGenerationScreen(),
        '/image_generation': (context) => const ImageGenerationScreen(),
        '/checker': (context) => const CheckerScreen(),
      },
    );
  }
}