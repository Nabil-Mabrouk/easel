<script setup>
import { ref } from 'vue';

const form = ref({
  painting_id: 'starry_night',
  child_name: 'Emma',
  child_age: 6,
  family_value: 'sharing'
});

const isLoading = ref(false);
const error = ref(null);
const downloadUrl = ref(null);

// --- NOUVEAU : Logique pour l'indicateur de progression ---
const displayStatus = ref('');
let statusInterval = null;

const statusMessages = [
  "Contacting the AI artist...",
  "Extracting artistic features from the painting...",
  "Creating a unique story outline...",
  "Writing the first chapters...",
  "Generating the cover image (1/7)...",
  "Generating scene image (2/7)...",
  "Generating scene image (3/7)...",
  "Generating scene image (4/7)...",
  "Generating scene image (5/7)...",
  "Generating scene image (6/7)...",
  "Generating the back cover (7/7)...",
  "Assembling the pages into a PDF book...",
  "Almost there, finalizing your book..."
];

const startStatusUpdates = () => {
  let messageIndex = 0;
  displayStatus.value = statusMessages[messageIndex];

  // Change le message toutes les 8 secondes
  statusInterval = setInterval(() => {
    messageIndex++;
    if (messageIndex < statusMessages.length) {
      displayStatus.value = statusMessages[messageIndex];
    } else {
      // Reste sur le dernier message si le backend prend plus de temps que prévu
      clearInterval(statusInterval);
    }
  }, 8000); // 8 secondes par étape est une bonne estimation
};

const stopStatusUpdates = () => {
  clearInterval(statusInterval);
  displayStatus.value = '';
};
// --- FIN DE LA NOUVELLE LOGIQUE ---


const API_URL = '/api/generate';

const generateBook = async () => {
  isLoading.value = true;
  error.value = null;
  downloadUrl.value = null;
  stopStatusUpdates(); // Réinitialise au cas où
  startStatusUpdates(); // Démarre l'affichage des messages

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    });

    if (!response.ok) {
      const errData = await response.text(); // Lire en texte pour voir si c'est du HTML
      try {
        // Essayer de parser comme JSON
        const jsonError = JSON.parse(errData);
        throw new Error(jsonError.detail || 'An unknown error occurred.');
      } catch (e) {
        // Si ce n'est pas du JSON, c'est probablement une erreur de serveur (timeout, etc.)
        throw new Error(`The server returned an error page. This is often a timeout issue. Please try again.`);
      }
    }

    const result = await response.json();
    downloadUrl.value = result.download_url;

  } catch (err) {
    error.value = `Failed to generate book: ${err.message}`;
  } finally {
    isLoading.value = false;
    stopStatusUpdates(); // Arrête l'affichage des messages à la fin
  }
};
</script>

<template>
  <div class="bg-gray-900 min-h-screen flex items-center justify-center font-sans p-4 text-white">
    <div class="w-full max-w-lg bg-gray-800 rounded-2xl shadow-lg p-8">
      
      <h1 class="text-4xl font-bold text-center mb-2 text-indigo-400">Easel AI</h1>
      <p class="text-center text-gray-400 mb-8">Create a Personalized Kids' Book from a Masterpiece</p>
      
      <!-- N'affiche le formulaire que si la génération n'est pas en cours -->
      <form @submit.prevent="generateBook" v-if="!isLoading">
        <div class="space-y-6">
          <div>
            <label for="painting" class="block text-sm font-medium text-gray-300">Choose a Painting</label>
            <select id="painting" v-model="form.painting_id" class="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
              <option value="starry_night">Van Gogh's Starry Night</option>
              <option value="mona_lisa">Da Vinci's Mona Lisa</option>
              <option value="the_scream">Munch's The Scream</option>
            </select>
          </div>
          <div>
            <label for="child_name" class="block text-sm font-medium text-gray-300">Child's Name</label>
            <input type="text" id="child_name" v-model="form.child_name" required class="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>
          <div class="grid grid-cols-2 gap-6">
            <div>
              <label for="child_age" class="block text-sm font-medium text-gray-300">Age</label>
              <input type="number" id="child_age" v-model.number="form.child_age" min="1" max="12" required class="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
            </div>
            <div>
              <label for="family_value" class="block text-sm font-medium text-gray-300">A Value to Teach</label>
              <input type="text" id="family_value" v-model="form.family_value" required class="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
            </div>
          </div>
        </div>
        <div class="mt-10">
          <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <span>Generate Book</span>
          </button>
        </div>
      </form>

      <!-- Affiche la progression à la place du formulaire -->
      <div v-if="isLoading" class="text-center">
        <svg class="animate-spin mx-auto h-12 w-12 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-300">Generating Your Storybook...</h3>
        <p class="mt-2 text-sm text-indigo-400 font-mono">{{ displayStatus }}</p>
      </div>

      <!-- Affiche le résultat/erreur après la génération -->
      <div v-if="!isLoading">
        <div v-if="error" class="mt-6 p-4 bg-red-900/50 text-red-300 rounded-md text-center">
          {{ error }}
        </div>
        <div v-if="downloadUrl" class="mt-6 p-4 bg-green-900/50 text-green-300 rounded-md text-center">
          <h3 class="font-semibold">Your book is ready!</h3>
          <a :href="downloadUrl" target="_blank" class="underline hover:text-green-100 font-bold mt-2 inline-block">Download PDF</a>
        </div>
      </div>

    </div>
  </div>
</template>