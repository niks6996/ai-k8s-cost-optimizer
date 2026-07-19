# AI-Powered Kubernetes Cost and Performance Optimizer

## Project Overview

This project is a lightweight, real-world style DevOps and Platform Engineering portfolio project.

The goal is to build a Kubernetes cost and performance optimisation tool that analyses workload CPU and memory usage, detects over-provisioned resources, and generates practical optimisation recommendations.

The project starts with mock Kubernetes metrics and gradually evolves into a cloud-native platform using Docker, Kubernetes, Terraform, GitHub Actions, Helm, ArgoCD, DevSecOps scanning, and monitoring with Prometheus and Grafana.

## Problem Statement

In Kubernetes environments, teams often request more CPU and memory than their applications actually use. This causes unnecessary cloud cost, poor resource efficiency, and operational waste.

This project demonstrates how platform engineers can analyse resource usage, improve workload efficiency, and build automation around cost optimisation.

## Key Features

- Mock Kubernetes metrics analysis
- CPU and memory optimisation recommendations
- Dockerised application
- Kubernetes deployment manifests
- CI/CD pipeline using GitHub Actions
- Infrastructure as Code using Terraform
- Helm chart packaging
- GitOps deployment using ArgoCD
- Security scanning using DevSecOps tools
- Monitoring and dashboards using Prometheus and Grafana

## Technology Stack

- Python
- JSON
- YAML
- Docker
- Kubernetes
- GitHub Actions
- Terraform
- Helm
- ArgoCD
- Trivy
- Checkov
- Prometheus
- Grafana

## High-Level Architecture

```text
Developer
   |
   v
GitHub Repository
   |
   v
CI/CD Pipeline
   |
   v
Docker Image
   |
   v
Kubernetes Cluster
   |
   v
Optimizer Application
   |
   v
Metrics Analysis and Recommendations
   |
   v
Monitoring and Reporting
