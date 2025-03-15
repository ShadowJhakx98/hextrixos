import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.158.0/examples/jsm/loaders/GLTFLoader.js';
// Global variables for Three.js scene
let scene, camera, renderer, model;
const loader = new THREE.GLTFLoader();
let rotationAngle = 0;

function initThreeJS() {
    // 1. Create the Scene
    scene = new THREE.Scene();

    // 2. Create and Configure the Camera
    const aspectRatio = window.innerWidth / window.innerHeight;
    camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);
    camera.position.z = 5;

    // 3. Create and configure the Renderer
    renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('brainCanvas'), alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0); // Set clear color to transparent black
    // Append Renderer to DOM
    document.body.appendChild(renderer.domElement);

    // 4. Lighting
    const directionalLight = new THREE.DirectionalLight(0x00ffff, 0.7); // Cyan directional light
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    const ambientLight = new THREE.AmbientLight(0x00ffff, 0.2); // Soft ambient light
    scene.add(ambientLight);

     // 5. Load the GLB Model
     loader.load('assets/beautiful_girl_3d_model.glb', function (gltf) {
         model = gltf.scene;
         console.log("The model has loaded!");
         // Apply holographic material - REPLACE THIS WITH A SHADER APPROACH
         model.traverse((child) => {
             if (child.isMesh) {
                 child.material = new THREE.MeshBasicMaterial({
                     color: 0x00ffff,
                     transparent: true,
                     opacity: 0.7,
                     wireframe: true,
                 });
             }
         });
         scene.add(model); //Add Model to scene
     }, undefined, function (error) {
         console.error('An error happened while loading the GLB file', error);
     });

    // Handle Window Resize
    window.addEventListener('resize', () => {
        const newWidth = window.innerWidth;
        const newHeight = window.innerHeight;
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
        brainCenter.x = newWidth / 2;
        brainCenter.y = newHeight / 2;
     });
}

function animate() {
    requestAnimationFrame(animate);

    // Rotate the model
    if (model) {
        rotationAngle += 0.005;
        model.rotation.y = rotationAngle;
    }

    // Render the scene
    renderer.render(scene, camera);

     // Call other update and draw functions for the brain and canvas elements
     updateBrainMesh();
     drawBrainMesh();

     // Update and draw neural connections
     connections.forEach(conn => {
        conn.update();
        conn.draw();
     });
 // Update and draw neurons
 neurons.forEach(neuron => {
     neuron.update();
     neuron.draw();
 });
}

// Initialize before brain
document.addEventListener('DOMContentLoaded', () => {
    initThreeJS(); // Add Threejs Init.

});