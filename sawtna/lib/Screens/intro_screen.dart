import 'package:flutter/material.dart';
import '../widgets/custom_button.dart';
import 'intro2_screen.dart';

class IntroScreen extends StatelessWidget {
  const IntroScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 40),
              Image.asset("assets/images/content.png", height: 150),
              const SizedBox(height: 40),
              const Text(
                "Smart Content Generation",
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              const Text(
                "Generate text and images that avoid smart censorship",
                style: TextStyle(fontSize: 16, color: Colors.black54),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              CustomButton(
                text: "Next",
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const Intro2Screen()),
                  );
                }, buttonColor: Colors.amber,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
// import 'package:flutter/material.dart';

// class IntroScreen extends StatelessWidget {
//   const IntroScreen({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         backgroundColor: Colors.white,
//         elevation: 0,
//         actions: [
//           TextButton(
//             onPressed: () {
//               Navigator.pushReplacementNamed(context, '/login'); // Skip to login
//             },
//             child: const Text('Skip', style: TextStyle(color: Colors.grey)),
//           ),
//         ],
//       ),
//       body: Padding(
//         padding: const EdgeInsets.all(20.0),
//         child: Column(
//           mainAxisAlignment: MainAxisAlignment.center,
//           children: [
//             Image.asset(
//               'assets/images/content.png', // Replace with your image
//               height: 200,
//             ),
//             const SizedBox(height: 40),
//             const Text(
//               'Smart Content Generation',
//               style: TextStyle(
//                 fontSize: 24,
//                 fontWeight: FontWeight.bold,
//               ),
//               textAlign: TextAlign.center,
//             ),
//             const SizedBox(height: 20),
//             const Text(
//               'Generate text and images that automart censorship.',
//               style: TextStyle(
//                 fontSize: 16,
//                 color: Colors.grey,
//               ),
//               textAlign: TextAlign.center,
//             ),
//             const Spacer(),
//             Row(
//               mainAxisAlignment: MainAxisAlignment.spaceBetween,
//               children: [
//                 // Container(
//                 //   width: 10,
//                 //   height: 10,
//                 //   decoration: BoxDecoration(
//                 //     color: Colors.red, // Active indicator
//                 //     borderRadius: BorderRadius.circular(5),
//                 //   ),
//                 // ),
//                 // Container(
//                 //   width: 10,
//                 //   height: 10,
//                 //   decoration: BoxDecoration(
//                 //     color: Colors.grey, // Inactive indicator
//                 //     borderRadius: BorderRadius.circular(5),
//                 //   ),
//                 // ),
//                 Expanded(
//                   child: Align(
//                     alignment: Alignment.centerRight,
//                     child: ElevatedButton(
//                       onPressed: () {
//                         Navigator.pushNamed(context, '/intro2');
//                       },
//                       style: ElevatedButton.styleFrom(
//                         backgroundColor: Colors.red,
//                         padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
//                         shape: RoundedRectangleBorder(
//                           borderRadius: BorderRadius.circular(30),
//                         ),
//                       ),
//                       child: const Text(
//                         'Next',
//                         style: TextStyle(fontSize: 18, color: Colors.white),
//                       ),
//                     ),
//                   ),
//                 ),
//               ],
//             ),
//           ],
//         ),
//       ),
//     );
//   }
// }