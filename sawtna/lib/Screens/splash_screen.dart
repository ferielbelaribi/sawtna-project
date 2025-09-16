// import 'package:flutter/material.dart';
// import '../widgets/custom_button.dart';
// import 'intro_screen.dart';

// class SplashScreen extends StatelessWidget {
//   const SplashScreen({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       body: Stack(
//         children: [
//           // الخلفية البيضا
//           Container(color: Colors.white),

//           // // دوائر حمرا فوق يسار
//           // Positioned(
//           //   top: -60,
//           //   left: -40,
//           //   child: Container(
//           //     height: 180,
//           //     width: 180,
//           //     decoration: const BoxDecoration(
//           //       color: Color(0xFFE57373), // لون أحمر فاتح
//           //       shape: BoxShape.circle,
//           //     ),
//           //   ),
//           // ),
//           // Positioned(
//           //   top: 20,
//           //   left: 80,
//           //   child: Container(
//           //     height: 100,
//           //     width: 100,
//           //     decoration: const BoxDecoration(
//           //       color: Color(0xFFFFCDD2), // وردي فاتح
//           //       shape: BoxShape.circle,
//           //     ),
//           //   ),
//           // ),
//            Positioned(
//         top: -60,
//         left: -40,
//         child: Container(
//           height: 180,
//           width: 180,
//           decoration: const BoxDecoration(
//             color: Color(0xFFC62828), // لون أحمر غامق للدويرة الكبيرة
//             shape: BoxShape.circle,
//           ),
//         ),
//       ),
//       Positioned(
//         top: 20,
//         left: 80,
//         child: Container(
//           height: 100,
//           width: 100,
//           decoration: const BoxDecoration(
//             color: Color(0xFFEF9A9A), // لون أحمر فاتح للدويرة الصغيرة
//             shape: BoxShape.circle,
//           ),
//         ),
//       ),

//           // المحتوى الرئيسي
//           Center(
//             child: Padding(
//               padding: const EdgeInsets.symmetric(horizontal: 20),
//               child: Column(
//                 mainAxisAlignment: MainAxisAlignment.center,
//                 children: [
//                   Image.asset("assets/images/logo.png", height: 160),
//                   const SizedBox(height: 20),
//                   const Text(
//                     "SAWTNA",
//                     style: TextStyle(
//                       fontSize: 26,
//                       fontWeight: FontWeight.bold,
//                       color: Colors.red,
//                       fontFamily: "Roboto", // ممكن تغيّري بالفونت المناسب
//                     ),
//                   ),
//                   const SizedBox(height: 10),
//                   const Text(
//                     "Keep the Palestinian voice alive",
//                     style: TextStyle(
//                       fontSize: 16,
//                       color: Colors.black54,
//                     ),
//                     textAlign: TextAlign.center,
//                   ),
//                   const SizedBox(height: 50),
//                   CustomButton(
//                     text: "Get Started",
//                     onPressed: () {
//                       Navigator.pushReplacement(
//                         context,
//                         MaterialPageRoute(builder: (_) => const IntroScreen()),
//                       );
//                     },
//                   ),
//                 ],
//               ),
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }
import 'package:flutter/material.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateToHome();
  }

  _navigateToHome() async {
    await Future.delayed(const Duration(milliseconds: 3000), () {}); // Simulate a delay
    Navigator.pushReplacementNamed(context, '/intro'); // Navigate to Intro screen
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // Or whatever background color you have
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Your logo/image for the splash screen
            Image.asset(
              'assets/images/logo.png', // Replace with your logo path
              height: 150,
            ),
            const SizedBox(height: 20),
            const Text(
              'SAWTNA',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            const Text(
              'Keep the Palestinian voice alive',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 50),
            ElevatedButton(
              onPressed: () {
                Navigator.pushReplacementNamed(context, '/intro');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red, // Button color
                padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
              ),
              child: const Text(
                'Get Started',
                style: TextStyle(fontSize: 18, color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}